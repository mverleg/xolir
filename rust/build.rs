
fn main() {
    tonic_build::configure()
        .build_server(false)
        .compile_protos(
            &["../proto/xolir/service.proto"],
            &["../proto"],  // imports
        )
        .expect("Failed to compile protos");

}
