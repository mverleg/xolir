
import os
from setuptools.command.build_py import build_py as build_py_orig

from setuptools.command.sdist import sdist as sdist_orig
import pathlib, shutil

class sdist_with_proto(sdist_orig):
    def make_release_tree(self, base_dir, files):
        super().make_release_tree(base_dir, files)
        repo_root = pathlib.Path(__file__).resolve().parents[2]
        repo_proto = repo_root / "proto"
        target = pathlib.Path(base_dir) / "proto"
        if repo_proto.exists():
            shutil.copytree(repo_proto, target, dirs_exist_ok=True)

class ProtocBuildCommand(build_py_orig):
    """Custom build_py to generate gRPC Python code before packaging."""

    def run(self):
        from grpc_tools import protoc
        proto_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "proto", "xolir"))
        proto_parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "proto"))
        out_dir = os.path.join(os.path.dirname(__file__), "xolir")
        os.makedirs(out_dir, exist_ok=True)

        for filename in os.listdir(proto_dir):
            if filename.endswith(".proto"):
                proto_file = os.path.join(proto_dir, filename)
                protoc.main([
                    "grpc_tools.protoc",
                    f"-I{proto_parent_dir}",
                    f"--python_out={out_dir}",
                    f"--grpc_python_out={out_dir}",
                    proto_file,
                ])
        super().run()

