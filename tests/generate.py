
from os import path
import sys

gen_pth = path.abspath(path.join(path.dirname(__file__), '../target/telir-python.zip'))
assert path.exists(gen_pth), f"run codegen to generate {gen_pth}"
sys.path.insert(0, gen_pth)

from telir.builtins_pb2 import *
from telir.debug_pb2 import *
from telir.expression_pb2 import *
from telir.function_pb2 import *
from telir.struct_pb2 import *
from telir.tel_pb2 import *
from telir.type_pb2 import *

