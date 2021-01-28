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
import pkgbuilder
import os
import sys

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

    print('\nInstallation directories')
    for d in INSTALLDIRS:
        value = getattr(build_conf, d)
        print('  %-24s %s' % (d, value if value else 'default'))

    print('\nTarget triplets')
    for d in ['build', 'host', 'target']:
        value = getattr(build_conf, d)
        print('  %-24s %s' % (d, value if value else 'default'))

    print('\nPackages to install')
    for d in build_conf.packages:
        print('  ' + d)

    pkgbuilder.setup_buildenv()
    builddir = os.getcwd()
    for d in build_conf.packages:
        pkg = pkgbuilder.get_pkg(d, build_conf, warn_installed=False)
        if pkg is not None:
            pkg.add_confirm_notes()
    print('\n'.join(pkgbuilder.confirm_notes))
    response = input('\nProceed with installation? [Y/n] ')
    if len(response) > 0 and response[0].lower() == 'n':
        print('Installation cancelled.')
        return
    print()
    for d in build_conf.packages:
        pkg = pkgbuilder.get_pkg(d, build_conf)
        if pkg is None:
            console.warn('skipping package `%s\'' % d)
            pkgbuilder.failures += 1
            os.chdir(builddir)
        elif d not in pkgbuilder.built:
            try:
                pkg.run()
            except ValueError:
                pkgbuilder.failures += 1
                console.warn('package `%s\' failed to build' % d)
            else:
                pkgbuilder.successes += 1
                pkgbuilder.built.append(d)
    print('\nFinished jobs.')
    print('  %-24s %d' % ('Succeeded', pkgbuilder.successes))
    print('  %-24s %d' % ('Failed', pkgbuilder.failures))

if __name__ == '__main__':
    if sys.version_info[1] < 4:
        console.error('this script requires at least Python 3.4')
    build_all()
