
# Xolir (Tel IR schema)

## Goal

Some languages, like [Tel](https://github.com/mverleg/tel), compile to multiple other languages. All the parsing and type checking is shared, but codegen is different.

To facilitate this, there needs to be a clear api that different code generator backends can consume. Since these backends may be different processes, it should be serializable.

That is Xolir - a cross-language intermediary representation (xo l ir). It is made for, but not restricted to, [Tel](https://github.com/mverleg/tel).

## Usage

The IR is specified in Protobuf3 format, with accompanying codegen.

### Artifacts

[Rust (cargo)](https://crates.io/crates/xolir):

```shell
cargo add xolir
```

[Python (pypi)](https://pypi.org/project/xolir/):

```shell
pip install xolir
```

[Java (nexus)](https://central.sonatype.com/artifact/nl.markv/xolir):

```xml
<dependency>
    <groupId>nl.markv</groupId>
    <artifactId>xolir</artifactId>
    <version>0.100.0</version>  <!-- check versions at https://central.sonatype.com/artifact/nl.markv/xolir -->
</dependency>
```

[Typescript (npm)](https://www.npmjs.com/package/xolir):

```shell
npm install xolir
```

You can also build locally with protoc:

```bash
bash run.sh test
```

## Implementation

Note that the language you generate the code for doesn't have to be the same language that the code generator is implemented in.

This uses protobuf. While this is not as descriptive as e.g. json-schema, this has better support for generating fast code in a range of languages.
