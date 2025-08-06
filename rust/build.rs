
fn main() {
    tonic_build::compile_protos("../proto/xolir/service.proto").unwrap();
}
