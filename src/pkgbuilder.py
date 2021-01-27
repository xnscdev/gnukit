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
import os
import shutil
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

def mkdir(name):
    try:
        os.mkdir(name)
    except OSError as e:
        if e.errno == errno.EEXIST:
            shutil.rmtree(name)
            try:
                os.mkdir(name)
            except OSError as e:
                console.error('failed to create directory `%s\': %s' %
                              (name, os.strerror(e.errno)))
        else:
            console.error('failed to create directory `%s\': %s' %
                          (name, os.strerror(e.errno)))

class Package:
    def __setup_build(self, config):
        if self.build == 'GNU':
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
        self.build = config['Package']['build']
        self.srcdir = config['Package']['srcdir']
        self.urls = config['URLs'].values()
        self.config = build_conf
        self.__setup_build(config)

    def fetch(self):
        for url in self.urls:
            try:
                with urllib.request.urlopen(url) as f:
                    data = f.read()
                with open('archive', 'wb') as f:
                    f.write(data)
            except HTTPError:
                pass # Try another URL
            else:
                return

    def extract(self):
        pass

    def configure(self):
        if self.build == 'GNU':
            conf_args = []
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
            conf_args = ' '.join(conf_args)
            print(conf_args)

    def build(self):
        pass

    def test(self):
        pass

    def run(self):
        print('Installing %s-%s' % (self.name, self.version))
        mkdir(self.name)
        os.chdir(self.name)
        self.fetch()
        self.extract()
        self.configure()
        os.chdir('..')

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
    try:
        shutil.rmtree('build')
    except FileNotFoundError:
        pass
    mkdir('build')
    os.chdir('build')
