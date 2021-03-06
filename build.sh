#!/bin/sh

# build.sh -- this file is part of gnukit.
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

# Wrapper shell script to run python build script

[ -z "$PYTHON" ] && PYTHON=python3
if [ -z "`$PYTHON --version 2>/dev/null`" ]; then
    echo "error: $PYTHON is not installed or does not work" 2>&1
    echo "       Please install python3 before running this script," 2>&1
    echo "       or set the PYTHON environment variable to a working" 2>&1
    echo "       python3 executable." 2>&1
    exit 1
fi

cd "`dirname $0`"
$PYTHON src/build.py
