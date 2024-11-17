
# Tel IR (schema)

## Goal

When the [Tel](https://github.com/mverleg/tel) compiler has done parsing, checking and other steps, it is time to generate executable code. 

The goal of Tel is to generate code in multiple languages. To make this easier, code generation backends in multiple languages are supported. This IR is the intermediate format that Tel generates and that backends consume.

## Usage

The IR is specified in Protobuf3 format.

While not as descriptive as e.g. json-schema, it has better support for generating fast code in a range of langauges.

```bash
rm -rf target/
mkdir -p ./target/java ./target/python ./target/rust
docker run -v"$(pwd)":/code -w /code rvolosatovs/protoc -I=. \
    --java_out=./target/java \
    --python_out=./target/python \
    --rust_out=experimental-codegen=enabled,kernel=cpp:./target/rust \
    telir/*.proto
```

