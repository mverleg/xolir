
# Tel IR (schema)

This provides the json schema that describes the intermediate representation (IR) for [Tel](https://github.com/mverleg/tel).

By having a json schema for the IR, the backend codegen does not need to be in the same langauge as the frontend. Most popular languages can take in the IR as json, and do the code generation.

This cna perhaps be made easier by generating a parser and dataclasses from the schema, like

* Rust: https://github.com/oxidecomputer/typify
* Java: https://stackoverflow.com/questions/72025422/how-to-generate-classes-out-of-the-json-schema
