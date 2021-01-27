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

from build import INSTALLDIRS
import configparser
import console

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

class Package:
    def __setup_build(self, config):
        if self.build == 'GNU':
            self.configure_args = config['build.GNU']['configure_args']
        else:
            console.error('invalid build system specified for package `%s\'' %
                          self.name)
            raise ValueError

    def __init__(self, name):
        config = configparser.ConfigParser(interpolation=
                                           configparser.ExtendedInterpolation())
        if not config.read('pkg/%s.conf' % name):
            console.warn('no package `%s\' found in registry' % name)
            raise ValueError
        self.name = config['Package']['name']
        self.version = config['Package']['version']
        self.build = config['Package']['build']
        self.urls = config['URLs'].values()
        self.__setup_build(config)

def get_pkg(name):
    try:
        pkg = Package(name)
    except ValueError:
        pass
    except KeyError:
        console.error('package `%s\' metadata missing required fields' % name)
    else:
        return pkg
    return None

def config(pkg, build_conf):
    if pkg.build == 'GNU':
        configure_args = []
        for k, v in GNU_INSTALLDIRS.items():
            value = getattr(build_conf, k)
            if value:
                arg = '%s=%s' % (v, value)
                if k == 'docdir':
                    arg += '/%s-%s' % (pkg.name, pkg.version)
                configure_args.append(arg)
        configure_args.extend(pkg.configure_args.split())
        configure_args = ' '.join(configure_args)
        print(configure_args)
    else:
        raise ValueError

def build(pkg):
    pass

def test(pkg):
    pass

def run(pkg, build_conf):
    print('Installing %s-%s' % (pkg.name, pkg.version))
    config(pkg, build_conf)
