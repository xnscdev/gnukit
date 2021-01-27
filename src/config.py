# config.py -- this file is part of gnukit.
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

def set_from(self, prop, attr, path):
    try:
        if path and len(prop[attr]) > 0 and prop[attr][0] != '/':
            console.error('property `%s\' requires an absolute path' % attr)
        setattr(self, attr, prop[attr])
    except KeyError:
        setattr(self, attr, '')

class BuildConfig:
    def __init__(self):
        config = configparser.ConfigParser(interpolation=
                                           configparser.ExtendedInterpolation())
        if not config.read('build.conf'):
            console.error('couldn\'t read configuration file `build.conf\'')
        try:
            install_dirs = config['InstallDirs']
        except AttributeError:
            console.error('config file missing required section `InstallDirs\'')
        try:
            targets = config['Targets']
        except AttributeError:
            console.error('config file missing required section `Targets\'')
        try:
            packages = config['Packages']
        except AttributeError:
            console.error('config file missing required section `Packages\'')

        # Set configuration file data
        set_from(self, install_dirs, 'prefix', True)
        set_from(self, install_dirs, 'eprefix', True)
        set_from(self, install_dirs, 'bindir', True)
        set_from(self, install_dirs, 'sbindir', True)
        set_from(self, install_dirs, 'libexecdir', True)
        set_from(self, install_dirs, 'sysconfdir', True)
        set_from(self, install_dirs, 'sharedstatedir', True)
        set_from(self, install_dirs, 'localstatedir', True)
        set_from(self, install_dirs, 'runstatedir', True)
        set_from(self, install_dirs, 'libdir', True)
        set_from(self, install_dirs, 'includedir', True)
        set_from(self, install_dirs, 'datadir', True)
        set_from(self, install_dirs, 'infodir', True)
        set_from(self, install_dirs, 'localedir', True)
        set_from(self, install_dirs, 'mandir', True)
        set_from(self, install_dirs, 'docdir', True)
        set_from(self, targets, 'build', False)
        set_from(self, targets, 'host', False)
        set_from(self, targets, 'target', False)

        # Set list of packages
        try:
            self.packages = packages['packages'].split()
        except KeyError:
            console.error('no packages to build, specify packages with the\n' +
                          '`packages\' variable in the `Packages\' section\n' +
                          'of the configuration file')
        try:
            self.run_tests = packages['tests'] == 'true'
        except KeyError:
            self.run_tests = False
