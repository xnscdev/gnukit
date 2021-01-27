# console.py -- this file is part of gnukit.
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

import sys

def error(msg):
    text = list(filter(lambda x: x, msg.splitlines()))
    if len(text) < 1:
        sys.exit(1)
    print('error:', text[0], file=sys.stderr)
    for l in text[1:]:
        print('      ', l, file=sys.stderr)
    sys.exit(1)

def warn(msg):
    text = list(filter(lambda x: x, msg.splitlines()))
    if len(text) < 1:
        return
    print('warning:', text[0], file=sys.stderr)
    for l in text[1:]:
        print('        ', l, file=sys.stderr)
