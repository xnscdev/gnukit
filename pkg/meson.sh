set -e

[ $# -eq 1]
cd ../meson-$VERSION # Build fails unless in srcdir
if [ "$1" = build ]; then
    python3 setup.py build
elif [ "$1" = test ]; then
    true
elif [ "$1" = install ]; then
    python3 setup.py install
fi
