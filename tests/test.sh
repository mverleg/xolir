#!/usr/bin/env -S bash -eEu -o pipefail

# user must run ../build.sh first

echo 'generating sample xolir'
base="$(realpath "${BASH_SOURCE%/*}")"
xolir_pth="$base/euler2.xolir"

# Must have:
# pip install protobuf
# pip install -e "$(git rev-parse --show-toplevel)/target/python"
python3 "$base/create_euler2_xolir.py"

if [ -z ${SKIP_INSTALL+x} ] ; then
  (
    echo 'installing java xolir'
    cd "$base/../target/java"
    time mvn install --offline -q -T1C -Pfat-jar -Drevision=test-SNAPSHOT
  )
else
  echo "skipping installing java xolir"
fi
(
  echo 'compiling sample xolir to java'
  cd "$base/generate_java"
  MAVEN_OPTS="-ea" mvn compile exec:java -e -q -Dexec.args="$xolir_pth"
)

echo done
