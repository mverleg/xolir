
fn main() {
    // Check if we're in a packaged environment (proto files are in the package root)
    let proto_dir = if std::path::Path::new("proto").exists() {
        "proto"
    } else {
        "../proto"
    };
    
    let service_proto = format!("{}/xolir/service.proto", proto_dir);
    
    tonic_build::configure()
        .build_server(false)
        .compile_protos(
            &[&service_proto],
            &[proto_dir],  // imports
        )
        .expect("Failed to compile protos");

}
