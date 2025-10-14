#!/usr/bin/env -S bash -eEu -o pipefail

# should probably run from virtualenv

base="$(dirname "$(basename "$0")")"
proto_dir="$(realpath "$base/../proto")"

pip install grpcio-tools

readarray -d '' protos < <(find "$proto_dir" -name "*.proto" -print0)

if (( ${#protos[@]} == 0 )); then
    echo "No .proto files found under $base/../proto" >&2
    exit 1
fi

python -m grpc_tools.protoc \
    -I"$proto_dir" \
    --python_out="$base" \
    --grpc_python_out="$base" \
   "${protos[@]}"

touch "$base/xolir/__init__.py"

cp "$base/../README.md" .

