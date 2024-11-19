
from os import path
import sys

gen_pth = path.abspath(path.join(path.dirname(__file__), '../target/telir-python.zip'))
assert path.exists(gen_pth), f"run codegen to generate {gen_pth}"
sys.path.insert(0, gen_pth)

from telir.type_pb2 import TypeRef, TypedName
from telir.struct_pb2 import Struct
from telir.function_pb2 import Function
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
    structs=[
        Struct(),
    ],
    functions=[
        Function(
            id=0,
            name="main",
            args=[],
            results=[TypeRef()],
        ),
        Function(
            id=0,
            name="euler",
            args=[TypedName("max", TypeRef())],
            results=[TypeRef()],
        ),
    ],
)
print(prog)
print(prog.SerializeToString())

