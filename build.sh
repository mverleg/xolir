#!/usr/bin/env -S bash -eEu -o pipefail

if [ $# != 0 ] || [ "${1:-}" == "-h" ]; then
    panic-in "$0" 'invokes ptoroc for codegen and does some bookkeeping; expects no arguments'
fi

PYTHON_BASE=./target/python
PYTHON_SRC="$PYTHON_BASE/telir"
JAVA_BASE=./target/java
JAVA_SRC="$JAVA_BASE/src/main/java/telir"
JAVA_RESOURCE="$JAVA_BASE/src/main/resources"
RUST_BASE=./target/rust
RUST_SRC="$RUST_BASE/src"

mkdir -p "$PYTHON_SRC" "$JAVA_SRC" "$JAVA_RESOURCE" "$RUST_SRC"

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

target="$(pwd)/target"
(
    echo 'packing python'
    cd "$PYTHON_BASE"
    zip -rq "$target/telir-python.zip" .
)
(
    cd "$JAVA_BASE"
    echo 'compiling java'
    mvn package -q -Pfat-jar
    echo PWD=$JAVA_BASE cp target/*.jar "$target/"
    cp target/*.jar "$target/"
)
(
    cd "$RUST_BASE"
    zip -rq "$target/telir-rust.zip" .
)


