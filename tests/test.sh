#!/usr/bin/env -S bash -eEu -o pipefail

# user must run ../build.sh first

echo 'generating sample telir'
base="$(realpath "${BASH_SOURCE%/*}")"
telir_pth="$base/euler2.telir"

# must have `pip install protobuf`
python3 "$base/create_euler2_telir.py" "$telir_pth"

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
  MAVEN_OPTS="-ea" mvn compile exec:java -e -q -Dexec.args="$telir_pth"
)

echo done
