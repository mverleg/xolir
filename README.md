
# Tel IR (schema)

## Goal

When the [Tel](https://github.com/mverleg/tel) compiler has done parsing, checking and other steps, it is time to generate executable code. 

The goal of Tel is to generate code in multiple languages. To make this easier, code generation backends in multiple languages are supported. This IR is the intermediate format that Tel generates and that backends consume.

## Usage

The IR is specified in Protobuf3 format.

While not as descriptive as e.g. json-schema, it has better support for generating fast code in a range of langauges.

```bash
rm -rf target/ &&\
bash build.sh &&\
sudo chown $USER:$USER -R target/
```

