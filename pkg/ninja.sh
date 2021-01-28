set -e

[ $# -eq 1 ]
if [ "$1" = build ]; then
    python3 ../ninja-$VERSION/configure.py --bootstrap
elif [ "$1" = test ]; then
    ./ninja ninja_test
    ./ninja_test
elif [ "$1" = install ]; then
    install -v -D -m 755 ninja $BINDIR
fi
