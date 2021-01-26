#!/usr/bin/env python3

# build.py -- this file is part of gnukit.
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

import config
import console

INSTALLDIRS = [
    'prefix',
    'eprefix',
    'bindir',
    'sbindir',
    'libexecdir',
    'sysconfdir',
    'sharedstatedir',
    'localstatedir',
    'runstatedir',
    'libdir',
    'includedir',
    'datadir',
    'infodir',
    'localedir',
    'mandir',
    'docdir'
]

def build_all():
    build_conf = config.BuildConfig()

    print('Installation directories')
    for d in INSTALLDIRS:
        print('%-24s %s' % (d, getattr(build_conf, d)))

if __name__ == '__main__':
    build_all()
