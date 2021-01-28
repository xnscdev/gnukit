set -e

[ $# -eq 1 ]
JOBS=`python3 -c "import multiprocessing; print(multiprocessing.cpu_count())"`
if [ "$1" = configure ]; then
    ../$SRCDIR/config --prefix=$PREFIX
elif [ "$1" = build ]; then
    PATH=/usr/local/bin:/usr/bin make `test -n $JOBS && echo -j $JOBS`
elif [ "$1" = test ]; then
    PATH=/usr/local/bin:/usr/bin make `test -n $JOBS && echo -j $JOBS` test
elif [ "$1" = install ]; then
    make install
fi
