"""
semantic.py

Performs semantic analysis over the AST:
- builds and checks a symbol table
- enforces simple scoping / usage rules
- does very basic type checking (only int supported)
"""

from symbols import SymbolTable


class SemanticError(Exception):
    pass


def analyze(program):
    """
    Entry point for semantic analysis.
    Returns the global symbol table.
    """
    from nl_ast import Program as AstProgram

    if not isinstance(program, AstProgram):
        raise TypeError("Semantic analyzer expected a Program node")

    global_scope = SymbolTable()

    for stmt in program.statements:
        analyze_statement(stmt, global_scope)

    return global_scope


def analyze_statement(stmt, scope: SymbolTable):
    from nl_ast import (
        VarDeclaration,
        Assignment,
        PrintStatement,
        IfStatement,
        WhileStatement,
        Block,
    )

    if isinstance(stmt, VarDeclaration):
        name = stmt.name.name
        scope.define(name)
        analyze_expression(stmt.expr, scope)
        scope.assign(name)
    elif isinstance(stmt, Assignment):
        name = stmt.name.name
        scope.lookup(name)  # must exist
        analyze_expression(stmt.expr, scope)
        scope.assign(name)
    elif isinstance(stmt, PrintStatement):
        analyze_expression(stmt.expr, scope)
    elif isinstance(stmt, IfStatement):
        analyze_expression(stmt.condition, scope)
        for inner in stmt.then_block.statements:
            analyze_statement(inner, scope)
        if stmt.else_block is not None:
            for inner in stmt.else_block.statements:
                analyze_statement(inner, scope)
    elif isinstance(stmt, WhileStatement):
        analyze_expression(stmt.condition, scope)
        for inner in stmt.body.statements:
            analyze_statement(inner, scope)
    elif isinstance(stmt, Block):
        for inner in stmt.statements:
            analyze_statement(inner, scope)
    else:
        raise SemanticError(f"Unknown statement type: {type(stmt).__name__}")


def analyze_expression(expr, scope: SymbolTable):
    from nl_ast import NumberLiteral, Identifier, BinaryOp

    if isinstance(expr, NumberLiteral):
        return "int"

    if isinstance(expr, Identifier):
        # Must have been declared
        scope.lookup(expr.name)
        return "int"

    if isinstance(expr, BinaryOp):
        left_type = analyze_expression(expr.left, scope)
        right_type = analyze_expression(expr.right, scope)
        if left_type != "int" or right_type != "int":
            raise SemanticError("Only integer arithmetic is supported")
        return "int"

    raise SemanticError(f"Unknown expression type: {type(expr).__name__}")

