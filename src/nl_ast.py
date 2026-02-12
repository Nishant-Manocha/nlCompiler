"""
nl_ast.py

Defines the abstract syntax tree node classes for the NL language.
Separated from the standard library module name `ast` to avoid conflicts.
"""


class Node:
    """Base class for all AST nodes."""
    pass


class Program(Node):
    def __init__(self, statements):
        self.statements = statements  # list of statement nodes


class NumberLiteral(Node):
    def __init__(self, value):
        self.value = value  # int


class Identifier(Node):
    def __init__(self, name):
        self.name = name  # str


class BinaryOp(Node):
    def __init__(self, op, left, right):
        # op is one of "PLUS", "MINUS", "MUL", "DIV"
        self.op = op
        self.left = left
        self.right = right


class VarDeclaration(Node):
    def __init__(self, name, expr):
        # name is an Identifier node
        self.name = name
        self.expr = expr


class Assignment(Node):
    def __init__(self, name, expr):
        # name is an Identifier node
        self.name = name
        self.expr = expr


class PrintStatement(Node):
    def __init__(self, expr):
        self.expr = expr


class Block(Node):
    def __init__(self, statements):
        self.statements = statements  # list of statement nodes


class IfStatement(Node):
    def __init__(self, condition, then_block, else_block=None):
        # condition is an expression node, then_block and else_block are Blocks
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block


class WhileStatement(Node):
    def __init__(self, condition, body):
        # condition is an expression node, body is a Block
        self.condition = condition
        self.body = body

