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

class Package:
    def __init__(self, name):
        config = configparser.ConfigParser(interpolation=
                                           configparser.ExtendedInterpolation())
        if not config.read('pkg/%s.conf' % name):
            console.warn('no package `%s\' found in registry' % name)
            raise ValueError()
        self.name = config['Package']['name']
        self.version = config['Package']['version']
        self.build = config['Package']['build']

def get_pkg(name):
    try:
        pkg = Package(name)
    except ValueError:
        pass
    except AttributeError:
        console.error('package `%s\' metadata missing required fields' % name)
    else:
        return pkg
    return None

def config(pkg):
    pass

def build(pkg):
    pass
