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

def set_from(self, prop, attr):
    try:
        value = prop[attr]
        setattr(self, attr, value)
    except AttributeError:
        console.warn('config file missing `%s\', leaving as default value' %
                     attr)

class BuildConfig:
    def __init__(self):
        config = configparser.ConfigParser()
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

        # Set configuration file data
        set_from(self, install_dirs, 'prefix')
        set_from(self, install_dirs, 'eprefix')
        set_from(self, install_dirs, 'bindir')
        set_from(self, install_dirs, 'sbindir')
        set_from(self, install_dirs, 'libexecdir')
        set_from(self, install_dirs, 'sysconfdir')
        set_from(self, install_dirs, 'sharedstatedir')
        set_from(self, install_dirs, 'localstatedir')
        set_from(self, install_dirs, 'runstatedir')
        set_from(self, install_dirs, 'libdir')
        set_from(self, install_dirs, 'includedir')
        set_from(self, install_dirs, 'datadir')
        set_from(self, install_dirs, 'infodir')
        set_from(self, install_dirs, 'localedir')
        set_from(self, install_dirs, 'mandir')
        set_from(self, install_dirs, 'docdir')
        set_from(self, targets, 'build')
        set_from(self, targets, 'host')
        set_from(self, targets, 'target')
