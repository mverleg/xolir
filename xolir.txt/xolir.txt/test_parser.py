#!/usr/bin/env python3
"""
Test script for the XOLIR text format parser.
"""

import sys
from parse import parse

def main():
    """Test the parser with the example file."""
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "../example.xotxt"
    
    try:
        with open(file_path, 'r') as f:
            text = f.read()
        
        program = parse(text)
        
        print(f"Successfully parsed program: {program.program_name}")
        print(f"IR version: {program.ir_version}")
        print(f"TELC version: {program.telc_version}")
        print(f"Types: {len(program.types)}")
        print(f"Functions: {len(program.funcs)}")
        
        # Print more detailed information
        if program.types:
            print("\nTypes:")
            for i, type_def in enumerate(program.types):
                if hasattr(type_def.target, 'name'):
                    print(f"  {i+1}. {type_def.target.name} (pos: {type_def.pos.start}, len: {type_def.pos.length})")
                    if hasattr(type_def.target, 'fields'):
                        print("    Fields:")
                        for field in type_def.target.fields:
                            print(f"      - {field.name} (pos: {field.pos.start}, len: {field.pos.length})")
        
        if program.funcs:
            print("\nFunctions:")
            for i, func in enumerate(program.funcs):
                print(f"  {i+1}. {func.name} (pos: {func.pos.start}, len: {func.pos.length})")
                if func.typ and hasattr(func.typ, 'args'):
                    print("    Arguments:")
                    for arg in func.typ.args:
                        print(f"      - {arg.name} (pos: {arg.pos.start}, len: {arg.pos.length})")
                if func.typ and hasattr(func.typ, 'results'):
                    print("    Results:")
                    for result in func.typ.results:
                        print(f"      - TypeRef (pos: {result.pos.start}, len: {result.pos.length})")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()