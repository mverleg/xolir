#!/usr/bin/env -S bash -eEu -o pipefail

# user must run ../build.sh first

echo 'generating sample telir'
base="$(realpath "${BASH_SOURCE%/*}")"

# must have `pip install protobuf`
python3 "$base/create_euler2_telir.py"

if [ -z ${SKIP_INSTALL+x} ] ; then
  (
    echo 'installing java telir'
    cd "$base/../target/java"
    time mvn install --offline -q -T1C -Pfat-jar -Drevision=test-SNAPSHOT
  )
else
  echo "skipping installing java telir"
fi
(
  echo 'compiling sample telir to java'
  cd "$base/generate_java"
  mvn compile exec:java -q -Dexec.args="$base/euler2.telir"
)

echo done
