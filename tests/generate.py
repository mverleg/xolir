
from os import path
import sys

gen_pth = path.abspath(path.join(path.dirname(__file__), '../target/telir-python.zip'))
assert path.exists(gen_pth), f"run codegen to generate {gen_pth}"
sys.path.insert(0, gen_pth)

from telir.debug_pb2 import SourceFile
from telir.tel_pb2 import TelProgram

prog = TelProgram(
    program_name='hello_world',
    ir_version=1,
    telc_version=1,
    sources=[SourceFile(
        id=0,
        name='test',
        source='# some code here',
    ), SourceFile(
        id=1,
        name='test2',
        source='# some more code here',
    )],
    structs=[],
    functions=[],
)
print(prog)
print(prog.SerializeToString())

