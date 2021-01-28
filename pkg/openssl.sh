set -e

[ $# -eq 1 ]
JOBS=`sysctl -n hw.cpu`
if [ "$1" = configure ]; then
    ../$SRCDIR/config --prefix=$PREFIX
elif [ "$1" = build ]; then
    make -j $JOBS
elif [ "$1" = test ]; then
    make -j $JOBS test
elif [ "$1" = install ]; then
    make install
fi
