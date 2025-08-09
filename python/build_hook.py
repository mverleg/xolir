
import os
from setuptools.command.build_py import build_py as build_py_orig

class ProtocBuildCommand(build_py_orig):
    """Custom build_py to generate gRPC Python code before packaging."""

    def run(self):
        from grpc_tools import protoc
        proto_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "proto", "xolir"))
        out_dir = os.path.join(os.path.dirname(__file__), "xolir")
        os.makedirs(out_dir, exist_ok=True)

        for filename in os.listdir(proto_dir):
            if filename.endswith(".proto"):
                proto_file = os.path.join(proto_dir, filename)
                protoc.main([
                    "grpc_tools.protoc",
                    f"-I{proto_dir}",
                    f"--python_out={out_dir}",
                    f"--grpc_python_out={out_dir}",
                    proto_file,
                ])
        super().run()

