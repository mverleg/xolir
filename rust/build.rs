use ::std::path::Path;

fn main() {
    if !Path::new("proto").exists() {
        panic!("proto directory not found, make sure to run with e.g. `./cargo-proto build`");
    }
    tonic_build::configure()
        .build_server(false)
        .compile_protos(
            &["proto/xolir/service.proto"],
            &["proto"],  // imports
        )
        .expect("Failed to compile protos, make sure to run with e.g. `./cargo-proto build`");

}
