import sys

# Depends on python/dist/, install e.g.
# pip install -U "python/dist/xolir-$(cat VERSION)-py3-none-any.whl"

from xolir.builtin_type_pb2 import BuiltinType
from xolir.builtin_function_pb2 import BuiltinFunc
from xolir.refs_pb2 import TypeRef
from xolir.type_pb2 import TypedName
from xolir.struct_pb2 import Struct
from xolir.function_pb2 import Function
from xolir.expression_pb2 import Expression, Read, Store, Call, If, While, Return
from xolir.debug_pb2 import SourceFile
from xolir.tel_pb2 import TelProgram

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
        Struct(
            id=0,
            name="Point",
            fields=[
                TypedName(name="x", typ=TypeRef(builtin=BuiltinType.REAL_64)),
                TypedName(name="y", typ=TypeRef(builtin=BuiltinType.REAL_64)),
            ],
        ),
    ],
    functions=[
        Function(
            id=0,
            name="main",
            args=[],
            results=[TypeRef()],
            code=[
                Expression(call=Call(func_ix=1, arguments=[Expression(int=4_000_000)])),
                Expression(return_=Return(value=Expression(int=0))),
            ],
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
                            Expression(store=Store(var_ix=4,
                                value=Expression(call=Call(builtin=BuiltinFunc.ADD_S64, arguments=[
                                    Expression(read=Read(var_ix=2)), Expression(read=Read(var_ix=3))])))),
                            Expression(if_=If(
                                condition=Expression(call=Call(builtin=BuiltinFunc.EQ_S64, arguments=[
                                    Expression(call=Call(builtin=BuiltinFunc.MOD_S64, arguments=[
                                        Expression(read=Read(var_ix=4)), Expression(int=2)])),
                                    Expression(int=0)])),
                                code=[
                                    Expression(store=Store(var_ix=1,
                                        value=Expression(call=Call(builtin=BuiltinFunc.ADD_S64, arguments=[
                                            Expression(read=Read(var_ix=1)), Expression(read=Read(var_ix=4))])))),
                                ])),
                            Expression(store=Store(var_ix=2, value=Expression(read=Read(var_ix=3)))),
                            Expression(store=Store(var_ix=3, value=Expression(read=Read(var_ix=4)))),
                        ])),
                Expression(return_=Return(value=Expression(read=Read(var_ix=1)))),
            ],
        ),
    ],
)

print(prog)

assert len(sys.argv) >= 2, "first arg must be output path"
with open(sys.argv[1], 'wb+') as f:
    f.write(prog.SerializeToString())

