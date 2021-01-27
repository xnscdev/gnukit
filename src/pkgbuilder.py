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

    def __init__(self, name, build_conf):
        config = configparser.ConfigParser(interpolation=
                                           configparser.ExtendedInterpolation())
        if not config.read('pkg/%s.conf' % name):
            console.warn('no package `%s\' found in registry' % name)
            raise ValueError
        self.name = config['Package']['name']
        self.version = config['Package']['version']
        self.build = config['Package']['build']
        self.urls = config['URLs'].values()
        self.config = build_conf
        self.__setup_build(config)

    def fetch(self):
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
        self.fetch()
        self.configure()

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
