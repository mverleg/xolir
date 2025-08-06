
pub use proto::*;

mod proto {
    #![allow(non_camel_case_types)]
    tonic::include_proto!("xolir");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn implement_test() {
        Program {
            program_name: "Hello World".to_string(),
            files: vec![],
            types: vec![],
            funcs: vec![],
        };
    }
}
