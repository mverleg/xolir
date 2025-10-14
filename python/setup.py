
from setuptools import setup
from xolir.build_hook import ProtocBuildCommand, sdist_with_proto

setup(
    cmdclass={
        "build_py": ProtocBuildCommand,
        "sdist": sdist_with_proto,
    }
)
