
from os import path
import sys

gen_pth = path.abspath(path.join(path.dirname(__file__), '../target/telir-python.zip'))
assert path.exists(gen_pth), f"run codegen to generate {gen_pth}"
sys.path.insert(0, gen_pth)

from telir.builtin_type_pb2 import BuiltinType
from telir.type_pb2 import TypeRef, TypedName
from telir.struct_pb2 import Struct
from telir.function_pb2 import Function
from telir.debug_pb2 import SourceFile
from telir.tel_pb2 import TelProgram

# def euler(max):
#     sum = 0
#     first, second = 1, 1
#     while second < max:
#         new = first + second
#         if new % 2 == 0:
#             sum += new
#         first = second
#         second = new
#     print(sum)
prog = TelProgram(
    program_name='euler2',
    ir_version=1,
    telc_version=1,
    sources=[SourceFile(
        id=0,
        name='test',
        source='''
def even_fib_sub(max):
    sum = 0
    first, second = 1, 1
    while second < max:
        new = first + second
        if new % 2 == 0:
            sum += new
        first = second
        second = new
    print(sum)
''',
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
            name="even_fib_sub",
            args=[
                TypedName(name="max", typ=TypeRef(builtin=BuiltinType.S_INT_64))
            ],
            results=[
                TypeRef(builtin=BuiltinType.S_INT_64)
            ],
            locals=[
                TypedName(name="sum", typ=TypeRef(builtin=BuiltinType.S_INT_64)),
                TypedName(name="first", typ=TypeRef(builtin=BuiltinType.S_INT_64)),
                TypedName(name="second", typ=TypeRef(builtin=BuiltinType.S_INT_64)),
            ],
            code=[],
        ),
    ],
)

print(prog)
print(prog.SerializeToString())

