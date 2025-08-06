#!/usr/bin/env python3
"""
Parser for XOLIR text format.
This parser builds an AST and tracks the position (start and length) of each token in the file.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Union, Dict, Tuple, Any


# Position tracking for tokens
@dataclass
class Position:
    start: int  # Character offset from the beginning of the file
    length: int  # Length of the token in characters


# Base class for all AST nodes
@dataclass
class Node:
    pos: Position


# Enum for builtin types
class BuiltinType(Enum):
    S_INT_32 = 0
    S_INT_64 = 1
    REAL_64 = 2
    BOOL = 3


# AST nodes for type references
@dataclass
class TypeRefBuiltin(Node):
    builtin_type: BuiltinType


@dataclass
class TypeRefTypeId(Node):
    type_id: int


@dataclass
class TypeRef(Node):
    target: Union[TypeRefBuiltin, TypeRefTypeId]


# AST node for typed names (used in struct fields and function arguments)
@dataclass
class TypedName(Node):
    name: str
    type_id: TypeRef


# AST nodes for type definitions
@dataclass
class StructType(Node):
    name: str
    is_anonymous: bool
    fields: List[TypedName]


@dataclass
class TypeDef(Node):
    target: StructType  # For now, only supporting StructType


# AST nodes for functions
@dataclass
class FunctionType(Node):
    args: List[TypedName]
    results: List[TypeRef]


@dataclass
class Function(Node):
    name: str
    typ: FunctionType
    locals: List[TypedName]
    code: List  # Empty for now, as the example doesn't have code


# AST node for the entire program
@dataclass
class Program(Node):
    program_name: str
    ir_version: int
    telc_version: int
    types: List[TypeDef]
    funcs: List[Function]


# Token types for the lexer
class TokenType(Enum):
    LBRACE = auto()        # {
    RBRACE = auto()        # }
    LBRACKET = auto()      # [
    RBRACKET = auto()      # ]
    LPAREN = auto()        # (
    RPAREN = auto()        # )
    COMMA = auto()         # ,
    EQUALS = auto()        # =
    HASH = auto()          # #
    PERCENT = auto()       # %
    IDENTIFIER = auto()    # names, keywords
    STRING = auto()        # "string"
    NUMBER = auto()        # 123
    COMMENT = auto()       # // comment
    WHITESPACE = auto()    # spaces, tabs, newlines
    EOF = auto()           # end of file


@dataclass
class Token:
    type: TokenType
    value: str
    pos: Position


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> List[Token]:
        tokens = []
        while self.pos < len(self.text):
            # Skip whitespace
            if self.text[self.pos].isspace():
                start = self.pos
                while self.pos < len(self.text) and self.text[self.pos].isspace():
                    if self.text[self.pos] == '\n':
                        self.line += 1
                        self.column = 1
                    else:
                        self.column += 1
                    self.pos += 1
                tokens.append(Token(
                    TokenType.WHITESPACE,
                    self.text[start:self.pos],
                    Position(start, self.pos - start)
                ))
                continue

            # Comments
            if self.pos + 1 < len(self.text) and self.text[self.pos:self.pos+2] == '//':
                start = self.pos
                self.pos += 2
                self.column += 2
                while self.pos < len(self.text) and self.text[self.pos] != '\n':
                    self.pos += 1
                    self.column += 1
                tokens.append(Token(
                    TokenType.COMMENT,
                    self.text[start:self.pos],
                    Position(start, self.pos - start)
                ))
                continue

            # Single character tokens
            if self.text[self.pos] == '{':
                tokens.append(Token(
                    TokenType.LBRACE,
                    '{',
                    Position(self.pos, 1)
                ))
                self.pos += 1
                self.column += 1
                continue
            elif self.text[self.pos] == '}':
                tokens.append(Token(
                    TokenType.RBRACE,
                    '}',
                    Position(self.pos, 1)
                ))
                self.pos += 1
                self.column += 1
                continue
            elif self.text[self.pos] == '[':
                tokens.append(Token(
                    TokenType.LBRACKET,
                    '[',
                    Position(self.pos, 1)
                ))
                self.pos += 1
                self.column += 1
                continue
            elif self.text[self.pos] == ']':
                tokens.append(Token(
                    TokenType.RBRACKET,
                    ']',
                    Position(self.pos, 1)
                ))
                self.pos += 1
                self.column += 1
                continue
            elif self.text[self.pos] == '(':
                tokens.append(Token(
                    TokenType.LPAREN,
                    '(',
                    Position(self.pos, 1)
                ))
                self.pos += 1
                self.column += 1
                continue
            elif self.text[self.pos] == ')':
                tokens.append(Token(
                    TokenType.RPAREN,
                    ')',
                    Position(self.pos, 1)
                ))
                self.pos += 1
                self.column += 1
                continue
            elif self.text[self.pos] == ',':
                tokens.append(Token(
                    TokenType.COMMA,
                    ',',
                    Position(self.pos, 1)
                ))
                self.pos += 1
                self.column += 1
                continue
            elif self.text[self.pos] == '=':
                tokens.append(Token(
                    TokenType.EQUALS,
                    '=',
                    Position(self.pos, 1)
                ))
                self.pos += 1
                self.column += 1
                continue
            elif self.text[self.pos] == '#':
                tokens.append(Token(
                    TokenType.HASH,
                    '#',
                    Position(self.pos, 1)
                ))
                self.pos += 1
                self.column += 1
                continue
            elif self.text[self.pos] == '%':
                tokens.append(Token(
                    TokenType.PERCENT,
                    '%',
                    Position(self.pos, 1)
                ))
                self.pos += 1
                self.column += 1
                continue

            # String literals
            elif self.text[self.pos] == '"':
                start = self.pos
                self.pos += 1
                self.column += 1
                while self.pos < len(self.text) and self.text[self.pos] != '"':
                    if self.text[self.pos] == '\\' and self.pos + 1 < len(self.text):
                        self.pos += 2
                        self.column += 2
                    else:
                        self.pos += 1
                        self.column += 1
                if self.pos < len(self.text):  # Skip closing quote
                    self.pos += 1
                    self.column += 1
                tokens.append(Token(
                    TokenType.STRING,
                    self.text[start:self.pos],
                    Position(start, self.pos - start)
                ))
                continue

            # Numbers
            elif self.text[self.pos].isdigit():
                start = self.pos
                while self.pos < len(self.text) and self.text[self.pos].isdigit():
                    self.pos += 1
                    self.column += 1
                tokens.append(Token(
                    TokenType.NUMBER,
                    self.text[start:self.pos],
                    Position(start, self.pos - start)
                ))
                continue

            # Identifiers
            elif self.text[self.pos].isalpha() or self.text[self.pos] == '_':
                start = self.pos
                while self.pos < len(self.text) and (self.text[self.pos].isalnum() or self.text[self.pos] == '_'):
                    self.pos += 1
                    self.column += 1
                tokens.append(Token(
                    TokenType.IDENTIFIER,
                    self.text[start:self.pos],
                    Position(start, self.pos - start)
                ))
                continue

            # Unknown character
            else:
                raise ValueError(f"Unexpected character: {self.text[self.pos]} at line {self.line}, column {self.column}")

        # Add EOF token
        tokens.append(Token(
            TokenType.EOF,
            '',
            Position(self.pos, 0)
        ))

        return tokens


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        """Look at the current token without consuming it."""
        while self.pos < len(self.tokens) and self.tokens[self.pos].type in (TokenType.WHITESPACE, TokenType.COMMENT):
            self.pos += 1
        if self.pos >= len(self.tokens):
            return Token(TokenType.EOF, '', Position(0, 0))
        return self.tokens[self.pos]

    def consume(self) -> Token:
        """Consume the current token and return it."""
        token = self.peek()
        self.pos += 1
        return token

    def expect(self, token_type: TokenType) -> Token:
        """Expect a token of a specific type, consume and return it."""
        token = self.peek()
        if token.type != token_type:
            raise ValueError(f"Expected {token_type}, got {token.type}")
        return self.consume()

    def parse_program(self) -> Program:
        """Parse a Program node."""
        start_pos = self.peek().pos.start
        
        # Expect opening brace
        self.expect(TokenType.LBRACE)
        self.expect(TokenType.IDENTIFIER)  # Program
        
        # Parse program fields
        program_name = ""
        ir_version = 0
        telc_version = 0
        types = []
        funcs = []
        
        while self.peek().type != TokenType.RBRACE:
            field_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.EQUALS)
            
            if field_name == "program_name":
                token = self.expect(TokenType.STRING)
                program_name = token.value.strip('"')
                # Consume comma if present
                if self.peek().type == TokenType.COMMA:
                    self.consume()
            elif field_name == "ir_version":
                token = self.expect(TokenType.NUMBER)
                ir_version = int(token.value)
                # Consume comma if present
                if self.peek().type == TokenType.COMMA:
                    self.consume()
            elif field_name == "telc_version":
                token = self.expect(TokenType.NUMBER)
                telc_version = int(token.value)
                # Consume comma if present
                if self.peek().type == TokenType.COMMA:
                    self.consume()
            elif field_name == "types":
                types = self.parse_type_list()
                # Consume comma if present
                if self.peek().type == TokenType.COMMA:
                    self.consume()
            elif field_name == "funcs":
                funcs = self.parse_function_list()
                # Consume comma if present
                if self.peek().type == TokenType.COMMA:
                    self.consume()
            else:
                raise ValueError(f"Unknown field name: {field_name}")
        
        # Expect closing brace
        end_token = self.expect(TokenType.RBRACE)
        end_pos = end_token.pos.start + end_token.pos.length
        
        return Program(
            Position(start_pos, end_pos - start_pos),
            program_name,
            ir_version,
            telc_version,
            types,
            funcs
        )

    def parse_type_list(self) -> List[TypeDef]:
        """Parse a list of TypeDef nodes."""
        types = []
        
        # Expect opening bracket
        self.expect(TokenType.LBRACKET)
        
        while self.peek().type != TokenType.RBRACKET:
            types.append(self.parse_type_def())
            
            # If there's a comma, consume it
            if self.peek().type == TokenType.COMMA:
                self.consume()
            
            # Handle extra closing braces (syntax peculiarity)
            while self.peek().type == TokenType.RBRACE:
                self.consume()
        
        # Expect closing bracket
        self.expect(TokenType.RBRACKET)
        
        return types

    def parse_type_def(self) -> TypeDef:
        """Parse a TypeDef node."""
        start_pos = self.peek().pos.start
        
        # Parse target field
        self.expect(TokenType.IDENTIFIER)  # target
        self.expect(TokenType.EQUALS)
        
        # Parse oneof target
        self.expect(TokenType.HASH)
        target_type = self.expect(TokenType.IDENTIFIER).value
        
        if target_type == "struct":
            target = self.parse_struct_type()
        else:
            raise ValueError(f"Unsupported type target: {target_type}")
        
        end_pos = self.tokens[self.pos - 1].pos.start + self.tokens[self.pos - 1].pos.length
        
        return TypeDef(
            Position(start_pos, end_pos - start_pos),
            target
        )

    def parse_struct_type(self) -> StructType:
        """Parse a StructType node."""
        start_pos = self.peek().pos.start
        
        # Expect opening parenthesis and brace
        self.expect(TokenType.LPAREN)
        self.expect(TokenType.LBRACE)
        self.expect(TokenType.IDENTIFIER)  # StructType
        
        # Parse struct fields
        name = ""
        is_anonymous = False
        fields = []
        
        while self.peek().type != TokenType.RBRACE:
            field_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.EQUALS)
            
            if field_name == "name":
                token = self.expect(TokenType.STRING)
                name = token.value.strip('"')
                self.expect(TokenType.COMMA)
            elif field_name == "is_anonymous":
                token = self.expect(TokenType.IDENTIFIER)
                is_anonymous = token.value == "true"
                self.expect(TokenType.COMMA)
            elif field_name == "fields":
                fields = self.parse_typed_name_list()
            else:
                raise ValueError(f"Unknown field name: {field_name}")
        
        # Expect closing brace and parenthesis
        self.expect(TokenType.RBRACE)
        end_token = self.expect(TokenType.RPAREN)
        end_pos = end_token.pos.start + end_token.pos.length
        
        return StructType(
            Position(start_pos, end_pos - start_pos),
            name,
            is_anonymous,
            fields
        )

    def parse_typed_name_list(self) -> List[TypedName]:
        """Parse a list of TypedName nodes."""
        typed_names = []
        
        # Expect opening bracket
        self.expect(TokenType.LBRACKET)
        
        while self.peek().type != TokenType.RBRACKET:
            typed_names.append(self.parse_typed_name())
            
            # If there's a comma, consume it
            if self.peek().type == TokenType.COMMA:
                self.consume()
            
            # Handle extra closing braces (syntax peculiarity in the example)
            while self.peek().type == TokenType.RBRACE:
                self.consume()
        
        # Expect closing bracket
        self.expect(TokenType.RBRACKET)
        
        return typed_names

    def parse_typed_name(self) -> TypedName:
        """Parse a TypedName node."""
        start_pos = self.peek().pos.start
        
        # Expect opening brace
        self.expect(TokenType.LBRACE)
        self.expect(TokenType.IDENTIFIER)  # TypedName
        
        # Parse typed name fields
        name = ""
        type_id = None
        
        while self.peek().type != TokenType.RBRACE:
            field_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.EQUALS)
            
            if field_name == "name":
                token = self.expect(TokenType.STRING)
                name = token.value.strip('"')
                # Comma after name is optional
                if self.peek().type == TokenType.COMMA:
                    self.consume()
            elif field_name == "type_id":
                type_id = self.parse_type_ref()
                # Comma after type_id is optional
                if self.peek().type == TokenType.COMMA:
                    self.consume()
            else:
                raise ValueError(f"Unknown field name: {field_name}")
            
            # Handle extra closing braces (syntax peculiarity)
            while self.peek().type == TokenType.RBRACE:
                self.consume()
        
        # Expect closing brace
        end_token = self.expect(TokenType.RBRACE)
        end_pos = end_token.pos.start + end_token.pos.length
        
        return TypedName(
            Position(start_pos, end_pos - start_pos),
            name,
            type_id
        )

    def parse_type_ref(self) -> TypeRef:
        """Parse a TypeRef node."""
        start_pos = self.peek().pos.start
        
        # Expect opening brace
        self.expect(TokenType.LBRACE)
        self.expect(TokenType.IDENTIFIER)  # TypeRef
        
        # Parse target field
        self.expect(TokenType.IDENTIFIER)  # target
        self.expect(TokenType.EQUALS)
        
        # Parse oneof target
        self.expect(TokenType.HASH)
        target_type = self.expect(TokenType.IDENTIFIER).value
        
        if target_type == "builtin":
            target = self.parse_builtin_type()
        elif target_type == "type_id":
            target = self.parse_type_id()
        else:
            raise ValueError(f"Unsupported type ref target: {target_type}")
        
        # Handle extra closing parentheses (syntax peculiarity)
        while self.peek().type == TokenType.RPAREN:
            self.consume()
        
        # Expect closing brace
        end_token = self.expect(TokenType.RBRACE)
        end_pos = end_token.pos.start + end_token.pos.length
        
        return TypeRef(
            Position(start_pos, end_pos - start_pos),
            target
        )

    def parse_builtin_type(self) -> TypeRefBuiltin:
        """Parse a TypeRefBuiltin node."""
        start_pos = self.peek().pos.start
        
        # Expect opening parenthesis and brace
        self.expect(TokenType.LPAREN)
        self.expect(TokenType.LBRACE)
        self.expect(TokenType.IDENTIFIER)  # BuiltinType
        
        # Parse builtin type
        self.expect(TokenType.PERCENT)
        builtin_type_name = self.expect(TokenType.IDENTIFIER).value
        builtin_type = getattr(BuiltinType, builtin_type_name)
        
        # Expect closing brace and parenthesis
        self.expect(TokenType.RBRACE)
        end_token = self.expect(TokenType.RPAREN)
        end_pos = end_token.pos.start + end_token.pos.length
        
        return TypeRefBuiltin(
            Position(start_pos, end_pos - start_pos),
            builtin_type
        )

    def parse_type_id(self) -> TypeRefTypeId:
        """Parse a TypeRefTypeId node."""
        start_pos = self.peek().pos.start
        
        # Expect opening parenthesis
        self.expect(TokenType.LPAREN)
        
        # Parse type id
        token = self.expect(TokenType.NUMBER)
        type_id = int(token.value)
        
        # Expect closing parenthesis
        end_token = self.expect(TokenType.RPAREN)
        end_pos = end_token.pos.start + end_token.pos.length
        
        return TypeRefTypeId(
            Position(start_pos, end_pos - start_pos),
            type_id
        )

    def parse_function_list(self) -> List[Function]:
        """Parse a list of Function nodes."""
        functions = []
        
        # Expect opening bracket
        self.expect(TokenType.LBRACKET)
        
        while self.peek().type != TokenType.RBRACKET:
            functions.append(self.parse_function())
            
            # If there's a comma, consume it
            if self.peek().type == TokenType.COMMA:
                self.consume()
            
            # Handle extra closing braces (syntax peculiarity)
            while self.peek().type == TokenType.RBRACE:
                self.consume()
        
        # Expect closing bracket
        self.expect(TokenType.RBRACKET)
        
        return functions

    def parse_function(self) -> Function:
        """Parse a Function node."""
        start_pos = self.peek().pos.start
        
        # Expect opening brace
        self.expect(TokenType.LBRACE)
        self.expect(TokenType.IDENTIFIER)  # Function
        
        # Parse function fields
        name = ""
        typ = None
        locals = []
        code = []
        
        while self.peek().type != TokenType.RBRACE:
            field_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.EQUALS)
            
            if field_name == "name":
                token = self.expect(TokenType.STRING)
                name = token.value.strip('"')
                self.expect(TokenType.COMMA)
            elif field_name == "typ":
                typ = self.parse_function_type()
            elif field_name == "locals":
                locals = self.parse_typed_name_list()
                self.expect(TokenType.COMMA)
            elif field_name == "code":
                code = self.parse_code_list()
                self.expect(TokenType.COMMA)
            else:
                raise ValueError(f"Unknown field name: {field_name}")
        
        # Expect closing brace
        end_token = self.expect(TokenType.RBRACE)
        end_pos = end_token.pos.start + end_token.pos.length
        
        return Function(
            Position(start_pos, end_pos - start_pos),
            name,
            typ,
            locals,
            code
        )

    def parse_function_type(self) -> FunctionType:
        """Parse a FunctionType node."""
        start_pos = self.peek().pos.start
        
        # Expect opening brace
        self.expect(TokenType.LBRACE)
        self.expect(TokenType.IDENTIFIER)  # FunctionType
        
        # Parse function type fields
        args = []
        results = []
        
        while self.peek().type != TokenType.RBRACE:
            field_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.EQUALS)
            
            if field_name == "args":
                args = self.parse_typed_name_list()
                self.expect(TokenType.COMMA)
            elif field_name == "results":
                results = self.parse_type_ref_list()
                self.expect(TokenType.COMMA)
            else:
                raise ValueError(f"Unknown field name: {field_name}")
        
        # Expect closing brace
        end_token = self.expect(TokenType.RBRACE)
        end_pos = end_token.pos.start + end_token.pos.length
        
        return FunctionType(
            Position(start_pos, end_pos - start_pos),
            args,
            results
        )

    def parse_type_ref_list(self) -> List[TypeRef]:
        """Parse a list of TypeRef nodes."""
        type_refs = []
        
        # Expect opening bracket
        self.expect(TokenType.LBRACKET)
        
        while self.peek().type != TokenType.RBRACKET:
            type_refs.append(self.parse_type_ref())
            
            # If there's a comma, consume it
            if self.peek().type == TokenType.COMMA:
                self.consume()
            
            # Handle extra closing braces (syntax peculiarity)
            while self.peek().type == TokenType.RBRACE:
                self.consume()
        
        # Expect closing bracket
        self.expect(TokenType.RBRACKET)
        
        return type_refs

    def parse_code_list(self) -> List:
        """Parse a list of code expressions (empty for now)."""
        # Expect opening bracket
        self.expect(TokenType.LBRACKET)
        
        # Expect closing bracket (empty list)
        self.expect(TokenType.RBRACKET)
        
        return []


def parse(text: str) -> Program:
    """Parse XOLIR text format into an AST."""
    lexer = Lexer(text)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse_program()


def main():
    """Main function for testing."""
    import sys
    
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            text = f.read()
    else:
        text = sys.stdin.read()
    
    try:
        program = parse(text)
        print(f"Successfully parsed program: {program.program_name}")
        print(f"IR version: {program.ir_version}")
        print(f"TELC version: {program.telc_version}")
        print(f"Types: {len(program.types)}")
        print(f"Functions: {len(program.funcs)}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()