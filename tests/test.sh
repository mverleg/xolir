#!/usr/bin/env -S bash -eEu -o pipefail

# user must run ../build.sh first

echo 'generating sample telir'

python3 create_euler2_telir.py

echo 'compiling sample telir to java'

mvn package -q;  #TODO @mark: exec

