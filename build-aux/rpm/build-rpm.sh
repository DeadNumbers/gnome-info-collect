#!/bin/bash

RPMBUILD_DIR="$HOME/rpmbuild"
VERSION="1.0"
NAME="gnome-info-collect"
SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

cd "$SCRIPTPATH" || exit


mkdir -p "$NAME-$VERSION"

cp ../../client/client.py "$SCRIPTPATH/$NAME-$VERSION/$NAME.py"
cp ../../LICENSE "$SCRIPTPATH/$NAME-$VERSION/LICENSE"

tar -cvzf "$NAME-$VERSION.tar.gz" "$NAME-$VERSION/"


mkdir -p "$RPMBUILD_DIR/SPECS"
mkdir -p "$RPMBUILD_DIR/SOURCES"

cp "gnome-info-collect.spec" "$RPMBUILD_DIR/SPECS/$NAME.spec"
cp "$NAME-$VERSION.tar.gz" "$RPMBUILD_DIR/SOURCES/$NAME-$VERSION.tar.gz"

rm -r "$NAME-$VERSION/" ./*.tar.gz


cd "$RPMBUILD_DIR/SPECS/" || exit

rpmbuild -ba "$NAME.spec"