#!/usr/bin/env -S bash -eEu -o pipefail

# user must run ../build.sh first

echo 'generating sample telir'

# must have `pip install protobuf`
python3 "${BASH_SOURCE%/*}/create_euler2_telir.py"

(
  echo 'installing java telir'
  cd "${BASH_SOURCE%/*}/../target/java"
  mvn install -q -Pfat-jar -Drevision=test-SNAPSHOT
)
(
  echo 'compiling sample telir to java'
  cd "${BASH_SOURCE%/*}/generate_java"
  mvn compile exec:java
)

echo done
