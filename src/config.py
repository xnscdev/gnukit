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
