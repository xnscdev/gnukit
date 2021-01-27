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
import os
import shutil
import subprocess
import sys
import tarfile
import urllib.request

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

def exec_process(args):
    subprocess.check_call(args, stdout=sys.stdout, stderr=sys.stderr)

class Package:
    def __setup_build(self, config):
        if self.buildsys == 'GNU':
            self.configure_args = config['build.GNU']['configure_args']
        else:
            console.error('invalid build system specified for package `%s\'' %
                          self.name)
            raise ValueError

    def __init__(self, name, build_conf):
        config = configparser.ConfigParser(interpolation=
                                           configparser.ExtendedInterpolation())
        if not config.read('../pkg/%s.conf' % name):
            console.warn('no package `%s\' found in registry' % name)
            raise ValueError
        self.name = config['Package']['name']
        self.version = config['Package']['version']
        self.buildsys = config['Package']['build']
        self.srcdir = config['Package']['srcdir']
        self.md5 = config['Package']['md5']
        self.urls = config['URLs'].values()
        self.config = build_conf
        self.__setup_build(config)

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
            except HTTPError:
                pass # Try another URL
            else:
                return
        console.warn('package `%s\' could not be fetched' % self.name)
        raise HTTPError

    def extract(self):
        if os.path.isdir(self.srcdir):
            return
        if os.path.isfile(self.srcdir):
            os.unlink(self.srcdir)
        print('Extracting %s-%s' % (self.name, self.version))
        with tarfile.open('archive') as f:
            f.extractall('.')
        mkdir('build')

    def configure(self):
        print('\nConfiguring %s-%s' % (self.name, self.version))
        os.chdir('build')
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
                    conf_args.append(arg)
            conf_args.extend(self.configure_args.split())
            exec_process(conf_args)

    def build(self):
        print('\nBuilding %s-%s' % (self.name, self.version))
        exec_process(['make'])

    def test(self):
        pass

    def install(self):
        pass

    def run(self):
        cwd = os.getcwd()
        mkdir(self.name, empty=False)
        os.chdir(self.name)
        self.fetch()
        self.extract()
        self.configure()
        self.build()
        self.test()
        self.install()
        os.chdir(cwd)

def get_pkg(name, build_conf):
    try:
        pkg = Package(name, build_conf)
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
