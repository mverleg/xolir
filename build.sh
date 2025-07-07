#!/usr/bin/env -S bash -eEu -o pipefail

if [ $# != 0 ] || [ "${1:-}" == "-h" ]; then
    panic-in "$0" 'invokes ptoroc for codegen and does some bookkeeping; expects no arguments'
fi

VERSION=0.1.0

PYTHON_BASE=./target/python
PYTHON_SRC="$PYTHON_BASE/telir"
JAVA_BASE=./target/java
JAVA_SRC="$JAVA_BASE/src/main/java/telir"
JAVA_RESOURCE="$JAVA_BASE/src/main/resources"
RUST_BASE=./target/rust
RUST_SRC="$RUST_BASE/src"

mkdir -p "$PYTHON_SRC" "$JAVA_SRC" "$JAVA_RESOURCE" "$RUST_SRC"

bad_files=$(grep -EL '^syntax = "proto3";' telir/*.proto)
if [ -n "$bad_files" ]; then
    printf "Files without syntax 3:\n%s\n" "$bad_files" 1>&2
    exit 1
fi

bad_files=$(grep -EL '^package ' telir/*.proto)
if [ -n "$bad_files" ]; then
    printf "Files without package:\n%s\n" "$bad_files" 1>&2
    exit 1
fi

echo 'compiling protoc'
docker run --rm -v"$(pwd)":/code -w /code rvolosatovs/protoc -I=. \
    --python_out="$PYTHON_SRC/.." \
    --java_out="$JAVA_SRC" \
    --rust_out=experimental-codegen=enabled,kernel=cpp:"$RUST_SRC" \
    telir/*.proto

cp LICENSE.txt "$PYTHON_BASE/"
cp LICENSE.txt "$JAVA_BASE/"
cp LICENSE.txt "$JAVA_RESOURCE/"
cp LICENSE.txt "$RUST_BASE/"

cp -r static/* target

target="$(pwd)/target"q
(
    echo 'packing python'
    cd "$PYTHON_BASE"
    zip -rq "$target/telir-python.zip" .
)
(
    cd "$JAVA_BASE"
    echo 'compiling java'
    mvn package -q -Pfat-jar -Drevision=$VERSION
    cp target/*.jar "$target/"
)
(
    cd "$RUST_BASE"
    zip -rq "$target/telir-rust.zip" .
)

echo done

