from os import path
import sys

gen_pth = path.abspath(path.join(path.dirname(__file__), '../target/telir-python.zip'))
assert path.exists(gen_pth), f"run codegen to generate {gen_pth}"
sys.path.insert(0, gen_pth)

from telir.builtin_type_pb2 import BuiltinType
from telir.builtin_function_pb2 import BuiltinFunc
from telir.type_pb2 import TypeRef, TypedName
from telir.struct_pb2 import Struct
from telir.function_pb2 import Function
from telir.expression_pb2 import Expression, Read, Store, Call, If, While, Return
from telir.debug_pb2 import SourceFile
from telir.tel_pb2 import TelProgram

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
    return sum
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
                TypedName(name="max", typ=TypeRef(builtin=BuiltinType.S_INT_64)),  # 0
            ],
            results=[
                TypeRef(builtin=BuiltinType.S_INT_64)
            ],
            locals=[
                TypedName(name="sum", typ=TypeRef(builtin=BuiltinType.S_INT_64)),  # 1
                TypedName(name="first", typ=TypeRef(builtin=BuiltinType.S_INT_64)),  # 2
                TypedName(name="second", typ=TypeRef(builtin=BuiltinType.S_INT_64)),  # 3
                TypedName(name="new", typ=TypeRef(builtin=BuiltinType.S_INT_64)),  # 4
            ],
            code=[
                Expression(store=Store(var_ix=1, value=Expression(int=0))),
                Expression(store=Store(var_ix=2, value=Expression(int=1))),
                Expression(store=Store(var_ix=3, value=Expression(int=1))),
                Expression(
                    while_=While(
                        condition=Expression(call=Call(builtin=BuiltinFunc.LT_S64, arguments=[
                            Expression(read=Read(var_ix=3)), Expression(read=Read(var_ix=0))])),
                        code=[
                            Expression(store=Store(var_ix=2,
                                value=Expression(call=Call(builtin=BuiltinFunc.ADD_S64, arguments=[
                                    Expression(read=Read(var_ix=2)), Expression(read=Read(var_ix=3))])))),
                            Expression(if_=If(
                                condition=Expression(call=Call(builtin=BuiltinFunc.MOD_S64, arguments=[
                                    Expression(read=Read(var_ix=4)), Expression(int=2)])),
                                code=[
                                    Expression(store=Store(var_ix=1,
                                        value=Expression(call=Call(builtin=BuiltinFunc.ADD_S64, arguments=[
                                            Expression(read=Read(var_ix=1)), Expression(read=Read(var_ix=4))])))),
                                ])),
                            Expression(store=Store(var_ix=2, value=Expression(read=Read(var_ix=3)))),
                            Expression(store=Store(var_ix=3, value=Expression(read=Read(var_ix=4)))),
                        ])),
                Expression(return_=Return(var_ix=1)),
            ],
        ),
    ],
)

print(prog)
with open(f'{prog.program_name}.telir', 'wb+') as f:
    f.write(prog.SerializeToString())

