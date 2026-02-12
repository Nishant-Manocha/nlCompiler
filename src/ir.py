"""
ir.py

Defines a very simple intermediate representation (IR) and
conversion from AST to IR.
"""

from dataclasses import dataclass
from typing import Any, List, Union


IRValue = Any  # int | str | (op, left, right)


@dataclass
class IRAssign:
    target: str
    value: IRValue


@dataclass
class IRPrint:
    value: IRValue


@dataclass
class IRLabel:
    name: str


@dataclass
class IRGoto:
    label: str


@dataclass
class IRIfGoto:
    cond: IRValue
    label: str


class IRProgram:
    def __init__(self):
        self.instructions: List[Union[IRAssign, IRPrint, IRLabel, IRGoto, IRIfGoto]] = []

    def add(self, instr: Union[IRAssign, IRPrint, IRLabel, IRGoto, IRIfGoto]):
        self.instructions.append(instr)


def generate_ir(program):
    """
    Generate a very simple IR from the AST.

    Expressions are flattened using temporaries where needed, encoded as:
      (op, left, right)
    where op is one of "PLUS", "MINUS", "MUL", "DIV".
    """
    from nl_ast import (
        Program as AstProgram,
        NumberLiteral,
        Identifier,
        BinaryOp,
        VarDeclaration,
        Assignment,
        PrintStatement,
        IfStatement,
        WhileStatement,
        Block,
    )

    if not isinstance(program, AstProgram):
        raise TypeError("IR generator expected a Program node")

    ir = IRProgram()
    temp_counter = [0]
    label_counter = [0]

    def new_temp() -> str:
        temp_counter[0] += 1
        return f"t{temp_counter[0]}"

    def new_label(prefix: str = "L") -> str:
        label_counter[0] += 1
        return f"{prefix}{label_counter[0]}"

    def emit_expr(node) -> IRValue:
        if isinstance(node, NumberLiteral):
            return node.value
        if isinstance(node, Identifier):
            return node.name
        if isinstance(node, BinaryOp):
            left = emit_expr(node.left)
            right = emit_expr(node.right)
            op_tuple = (node.op, left, right)
            tmp = new_temp()
            ir.add(IRAssign(tmp, op_tuple))
            return tmp
        raise ValueError(f"Unsupported expression node in IR: {node!r}")

    def emit_block(block: Block):
        for inner in block.statements:
            emit_stmt(inner)

    def emit_stmt(stmt):
        if isinstance(stmt, VarDeclaration):
            value = emit_expr(stmt.expr)
            ir.add(IRAssign(stmt.name.name, value))
        elif isinstance(stmt, Assignment):
            value = emit_expr(stmt.expr)
            ir.add(IRAssign(stmt.name.name, value))
        elif isinstance(stmt, PrintStatement):
            value = emit_expr(stmt.expr)
            ir.add(IRPrint(value))
        elif isinstance(stmt, IfStatement):
            then_label = new_label("then")
            end_label = new_label("endif")
            if stmt.else_block is not None:
                else_label = new_label("else")
                cond_val = emit_expr(stmt.condition)
                ir.add(IRIfGoto(cond_val, then_label))
                ir.add(IRGoto(else_label))
                ir.add(IRLabel(then_label))
                emit_block(stmt.then_block)
                ir.add(IRGoto(end_label))
                ir.add(IRLabel(else_label))
                emit_block(stmt.else_block)
                ir.add(IRLabel(end_label))
            else:
                cond_val = emit_expr(stmt.condition)
                ir.add(IRIfGoto(cond_val, then_label))
                ir.add(IRGoto(end_label))
                ir.add(IRLabel(then_label))
                emit_block(stmt.then_block)
                ir.add(IRLabel(end_label))
        elif isinstance(stmt, WhileStatement):
            start_label = new_label("while_start")
            body_label = new_label("while_body")
            end_label = new_label("while_end")

            ir.add(IRLabel(start_label))
            cond_val = emit_expr(stmt.condition)
            ir.add(IRIfGoto(cond_val, body_label))
            ir.add(IRGoto(end_label))
            ir.add(IRLabel(body_label))
            emit_block(stmt.body)
            ir.add(IRGoto(start_label))
            ir.add(IRLabel(end_label))
        elif isinstance(stmt, Block):
            emit_block(stmt)
        else:
            raise ValueError(f"Unsupported statement node in IR: {stmt!r}")

    for stmt in program.statements:
        emit_stmt(stmt)

    return ir

