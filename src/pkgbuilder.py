# pkgbuilder.py -- this file is part of gnukit.
# Copyright (C) 2020 XNSC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import configparser
import console
import errno
import hashlib
import multiprocessing
import os
import shutil
import subprocess
import sys
import tarfile
import textwrap
import urllib.request

built = []
listed = []
confirm_notes = []
successes = 0
skips = 0
failures = 0

GNU_INSTALLDIRS = {
    'prefix': '--prefix',
    'eprefix': '--exec-prefix',
    'bindir': '--bindir',
    'sbindir': '--sbindir',
    'libexecdir': '--libexecdir',
    'sysconfdir': '--sysconfdir',
    'sharedstatedir': '--sharedstatedir',
    'localstatedir': '--localstatedir',
    'runstatedir': '--runstatedir',
    'libdir': '--libdir',
    'includedir': '--includedir',
    'datadir': '--datarootdir',
    'infodir': '--infodir',
    'localedir': '--localedir',
    'mandir': '--mandir',
    'docdir': '--docdir'
}

def mkdir(name, empty=True):
    if empty:
        try:
            shutil.rmtree(name)
        except FileNotFoundError:
            pass
    try:
        os.mkdir(name)
    except OSError as e:
        if e.errno == errno.EEXIST:
            return
        console.error('failed to create directory `%s\': %s' %
                      (name, os.strerror(e.errno)))

def exec_process(args, env=None):
    print(' '.join(args))
    if env:
        subprocess.check_call(args, stdout=sys.stdout, stderr=sys.stderr,
                              env=env)
    else:
        subprocess.check_call(args, stdout=sys.stdout, stderr=sys.stderr)

class AlreadyInstalled(RuntimeError):
    pass

class Package:
    def __setup_build(self, config):
        if self.buildsys == 'GNU':
            self.configure_args = config['build.GNU']['configure_args']
        elif self.buildsys == 'make':
            self.test_target = config['build.make']['test_target']
        elif self.buildsys == 'meson':
            self.meson_args = config['build.meson']['meson_args']
        else:
            console.error('invalid build system specified for package `%s\'' %
                          self.name)
            raise ValueError

    def __defattr(self, attr, default):
        value = getattr(self.config, attr)
        return '%s = %s' % (attr, value if value else default)

    def __gen_installdirs(self):
        ret = ['[InstallDirs]']
        ret.append(self.__defattr('prefix', '/usr/local'))
        ret.append(self.__defattr('eprefix', '${prefix}'))
        ret.append(self.__defattr('bindir', '${eprefix}/bin'))
        ret.append(self.__defattr('sbindir', '${eprefix}/sbin'))
        ret.append(self.__defattr('libexecdir', '${eprefix}/libexec'))
        ret.append(self.__defattr('sysconfdir', '${prefix}/etc'))
        ret.append(self.__defattr('sharedstatedir', '${prefix}/com'))
        ret.append(self.__defattr('localstatedir', '${prefix}/var'))
        ret.append(self.__defattr('runstatedir', '${localstatedir}/run'))
        ret.append(self.__defattr('libdir', '${eprefix}/lib'))
        ret.append(self.__defattr('includedir', '${prefix}/include'))
        ret.append(self.__defattr('datadir', '${prefix}/share'))
        ret.append(self.__defattr('infodir', '${datadir}/info'))
        ret.append(self.__defattr('localedir', '${datadir}/locale'))
        ret.append(self.__defattr('mandir', '${datadir}/man'))
        ret.append(self.__defattr('docdir', '${datadir}/doc'))
        return '\n'.join(ret)

    def __init__(self, name, build_conf, warn_installed=True):
        config = configparser.ConfigParser(interpolation=
                                           configparser.ExtendedInterpolation())
        self.config = build_conf
        config.read_string(self.__gen_installdirs())
        if not config.read('../pkg/%s.conf' % name):
            console.warn('no package `%s\' found in registry' % name)
            raise ValueError
        if os.path.isfile('../pkg/%s.patch' % name):
            self.patch = os.path.realpath('../pkg/%s.patch' % name)
        else:
            self.patch = None

        self.name = config['Package']['name']
        self.version = config['Package']['version']
        if warn_installed and os.path.isfile(config['Package']['installed']):
            console.warn('%s-%s appears to already be installed' %
                         (self.name, self.version))
            raise AlreadyInstalled

        self.buildsys = config['Package']['build']
        self.srcdir = config['Package']['srcdir']
        self.md5 = config['Package']['md5']
        self.dependencies = config['Package']['dependencies'].split()
        self.urls = config['URLs'].values()
        self.__setup_build(config)

        try:
            self.confirm_notes = config['Package']['notes']
        except KeyError:
            self.confirm_notes = None

        self.env = {}
        try:
            env = config['Package']['env'].split()
            for var in env:
                pair = var.split('=')
                self.env[pair[0]] = '='.join(pair[1:])
        except KeyError:
            pass

    def fetch(self):
        if os.path.isfile('archive'):
            with open('archive', 'rb') as f:
                md5 = hashlib.md5(f.read()).hexdigest()
            if md5 != self.md5:
                print('  Bad archive MD5 checksum, re-downloading')
                os.unlink('archive')
            else:
                return
        print('Downloading %s-%s' % (self.name, self.version))
        for url in self.urls:
            try:
                print('  Attempting to download archive from ' + url)
                with urllib.request.urlopen(url) as f:
                    data = f.read()
                md5 = hashlib.md5(data).hexdigest()
                if md5 != self.md5:
                    print('  Bad MD5 checksum: got ' + md5)
                    print('               expected ' + self.md5)
                    continue
                with open('archive', 'wb') as f:
                    f.write(data)
            except urllib.error.HTTPError:
                pass # Try another URL
            else:
                return
        console.warn('package `%s\' could not be fetched' % self.name)
        raise ValueError

    def extract(self):
        if os.path.isdir(self.srcdir):
            return
        if os.path.isfile(self.srcdir):
            os.unlink(self.srcdir)
        print('Extracting %s-%s' % (self.name, self.version))
        with tarfile.open('archive') as f:
            f.extractall('.')
        # Apply a patch, if any
        if self.patch is not None:
            os.chdir(self.srcdir)
            exec_process(['patch', '-p', '1', '-i', self.patch])
            os.chdir('..')
        mkdir('build')

    def configure(self):
        if self.buildsys == 'make':
            return
        print('\nConfiguring %s-%s' % (self.name, self.version))
        if self.buildsys == 'GNU':
            conf_args = ['../%s/configure' % self.srcdir]
            for d in ['build', 'host', 'target']:
                value = getattr(self.config, d)
                if value:
                    conf_args.append('--%s=%s' % (d, value))
            for k, v in GNU_INSTALLDIRS.items():
                value = getattr(self.config, k)
                if value:
                    arg = '%s=%s' % (v, value)
                    if k == 'docdir':
                        arg += '/%s-%s' % (self.name, self.version)
                    elif k == 'runstatedir':
                        pass # TODO Don't pass --runstatedir if unsupported
                    conf_args.append(arg)
            conf_args.extend(self.configure_args.split())
            exec_process(conf_args, self.env)
        elif self.buildsys == 'meson':
            conf_args = ['meson']
            # TODO Meson cross-compilation support
            for k, v in GNU_INSTALLDIRS.items():
                value = getattr(self.config, k)
                if value:
                    arg = '%s=%s' % (v, value)
                    # Options unsupported by meson
                    if k in ['runstatedir', 'docdir']:
                        continue
                    conf_args.append(arg)
            conf_args.extend(self.meson_args.split())
            conf_args.append('../' + self.srcdir)
            exec_process(conf_args, self.env)

    def build(self):
        os.chdir('build')
        if not os.path.isfile('config.status'):
            self.configure()
        print('\nBuilding %s-%s' % (self.name, self.version))
        if self.buildsys == 'GNU':
            exec_process(['make', '-j', str(multiprocessing.cpu_count())])
        elif self.buildsys == 'make':
            exec_process(['make', '-j', str(multiprocessing.cpu_count()),
                          '-C', '../' + self.srcdir])
        elif self.buildsys == 'meson':
            exec_process(['ninja', '-C', '../' + self.srcdir])

    def test(self):
        self.build()
        if not self.config.run_tests:
            return
        print('\nRunning unit tests for %s-%s' % (self.name, self.version))
        if self.buildsys == 'GNU':
            exec_process(['make', 'check'])
        elif self.buildsys == 'make':
            exec_process(['make', '-C', '../' + self.srcdir, self.test_target])
        elif self.buildsys == 'meson':
            exec_process(['ninja', '-C', '../' + self.srcdir, 'test'])

    def install(self):
        self.test()
        print('\nInstalling %s-%s' % (self.name, self.version))
        if self.buildsys == 'GNU':
            exec_process(['make', 'install'])
        elif self.buildsys == 'make':
            exec_process(['make', '-C', '../' + self.srcdir, 'install'])
        elif self.buildsys == 'meson':
            exec_process(['ninja', '-C', '../' + self.srcdir, 'install'])

    def add_confirm_notes(self):
        global confirm_notes
        for d in self.dependencies:
            if d in listed:
                continue
            dpkg = Package(d, self.config, warn_installed=False)
            if dpkg is not None:
                dpkg.add_confirm_notes()
        if self.name not in listed and self.confirm_notes is not None:
            confirm_notes.append('\n%s-%s:' % (self.name, self.version))
            lines = textwrap.wrap(self.confirm_notes, 74,
                                  break_long_words=False)
            confirm_notes.extend(['  ' + l for l in lines])
        listed.append(self.name)

    def run(self):
        global successes
        global skips
        global failures
        for d in self.dependencies:
            if d in built:
                continue
            try:
                dpkg = Package(d, self.config)
            except AlreadyInstalled:
                skips += 1
                built.append(d)
                continue
            if dpkg is None:
                failures += 1
                console.warn('unknown dependency ' + d)
                raise ValueError
            try:
                print('Attempting to build %s-%s dependency %s-%s' %
                      (self.name, self.version, dpkg.name, dpkg.version))
                dpkg.run()
            except:
                failures += 1
                console.warn('failed to build dependency %s-%s' %
                             (dpkg.name, dpkg.version))
                raise Exception
            else:
                successes += 1
                built.append(d)
        cwd = os.getcwd()
        mkdir(self.name, empty=False)
        os.chdir(self.name)
        self.fetch()
        self.extract()
        self.install()
        os.chdir(cwd)

def get_pkg(name, build_conf, warn_installed=True):
    try:
        pkg = Package(name, build_conf, warn_installed)
    except ValueError:
        pass
    except KeyError:
        console.error('package `%s\' metadata missing required fields' % name)
    else:
        return pkg
    return None

def setup_buildenv():
    mkdir('build', empty=False)
    os.chdir('build')
