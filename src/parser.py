"""
parser.py

Parses a token stream (from lexer.tokenize) into an AST (see nl_ast.py).
This is a straightforward recursive-descent parser for the NL language:

  program  ::= statement* EOF
  statement::= "let" IDENT "=" expr ";"
             | IDENT "=" expr ";"
             | "print" expr ";"
  expr     ::= term (("PLUS" | "MINUS") term)*
  term     ::= factor (("MUL" | "DIV") factor)*
  factor   ::= "MINUS" factor
             | primary
  primary  ::= NUMBER
             | IDENT
             | "(" expr ")"
"""

from __future__ import annotations

import json
import os
import time
from typing import List

from nl_ast import (
    Program,
    VarDeclaration,
    Assignment,
    PrintStatement,
    Identifier,
    NumberLiteral,
    BinaryOp,
    Block,
    IfStatement,
    WhileStatement,
)


class ParserError(Exception):
    pass


def _debug_log(hypothesis_id: str, location: str, message: str, data: dict, run_id: str = "post-fix") -> None:
    """
    Lightweight debug logger that appends NDJSON lines to .debug/debug.log.
    Safe to call; failures are silently ignored.
    """
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(base_dir, ".debug", "debug.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        entry = {
            "id": f"log_{int(time.time() * 1000)}",
            "timestamp": int(time.time() * 1000),
            "location": location,
            "message": message,
            "data": data,
            "runId": run_id,
            "hypothesisId": hypothesis_id,
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        # Never let logging break compilation
        pass
# endregion


class Parser:
    def __init__(self, tokens: List) -> None:
        self.tokens = tokens
        self.pos = 0

        # region agent log
        if self.tokens:
            first = self.tokens[0]
            _debug_log(
                hypothesis_id="H_parser_class",
                location="parser.py:Parser.__init__",
                message="Parser constructed",
                data={"first_token_type": first.type, "first_token_value": str(first.value)},
            )
        # endregion

    def current(self):
        return self.tokens[self.pos]

    def consume(self, expected_type: str):
        tok = self.current()
        if tok.type != expected_type:
            raise ParserError(
                f"Expected {expected_type}, got {tok.type} at line {tok.line}, column {tok.column}"
            )
        self.pos += 1
        return tok

    def match(self, expected_type: str):
        tok = self.current()
        if tok.type == expected_type:
            self.pos += 1
            return tok
        return None

    def parse(self) -> Program:
        # region agent log
        _debug_log(
            hypothesis_id="H_parser_flow",
            location="parser.py:Parser.parse",
            message="parse_start",
            data={"token_count": len(self.tokens)},
        )
        # endregion

        statements = []
        while self.current().type != "EOF":
            statements.append(self.parse_statement())
        return Program(statements)

    def parse_statement(self):
        tok = self.current()

        # If / if-else statement: if (expr) { ... } [else { ... }]
        if tok.type == "IF":
            self.consume("IF")
            self.consume("LPAREN")
            condition = self.parse_expression()
            self.consume("RPAREN")
            then_block = self.parse_block()
            else_block = None
            if self.current().type == "ELSE":
                self.consume("ELSE")
                else_block = self.parse_block()
            return IfStatement(condition, then_block, else_block)

        # While loop: while (expr) { ... }
        if tok.type == "WHILE":
            self.consume("WHILE")
            self.consume("LPAREN")
            condition = self.parse_expression()
            self.consume("RPAREN")
            body = self.parse_block()
            return WhileStatement(condition, body)

        # Variable declaration: let x = expr;
        if tok.type == "LET":
            self.consume("LET")
            ident = self.consume("IDENT")
            self.consume("ASSIGN")
            expr = self.parse_expression()
            self.consume("SEMICOLON")
            return VarDeclaration(Identifier(ident.value), expr)

        # Print statement: print expr;
        if tok.type == "PRINT":
            self.consume("PRINT")
            expr = self.parse_expression()
            self.consume("SEMICOLON")
            return PrintStatement(expr)

        # Assignment: x = expr;
        if tok.type == "IDENT":
            ident = self.consume("IDENT")
            self.consume("ASSIGN")
            expr = self.parse_expression()
            self.consume("SEMICOLON")
            return Assignment(Identifier(ident.value), expr)

        raise ParserError(
            f"Unexpected token {tok.type} at line {tok.line}, column {tok.column}"
        )

    # Expression parsing with precedence
    def parse_expression(self):
        return self.parse_term()

    def parse_block(self) -> Block:
        """Parse a block delimited by { }."""
        self.consume("LBRACE")
        statements = []
        while self.current().type != "RBRACE":
            statements.append(self.parse_statement())
        self.consume("RBRACE")
        return Block(statements)

    def parse_term(self):
        node = self.parse_factor()
        while self.current().type in ("PLUS", "MINUS"):
            op = self.current().type
            self.consume(op)
            right = self.parse_factor()
            node = BinaryOp(op, node, right)
        return node

    def parse_factor(self):
        node = self.parse_unary()
        while self.current().type in ("MUL", "DIV"):
            op = self.current().type
            self.consume(op)
            right = self.parse_unary()
            node = BinaryOp(op, node, right)
        return node

    def parse_unary(self):
        tok = self.current()
        if tok.type == "MINUS":
            self.consume("MINUS")
            expr = self.parse_unary()
            zero = NumberLiteral(0)
            return BinaryOp("MINUS", zero, expr)
        return self.parse_primary()

    def parse_primary(self):
        tok = self.current()
        if tok.type == "NUMBER":
            self.consume("NUMBER")
            return NumberLiteral(tok.value)
        if tok.type == "IDENT":
            self.consume("IDENT")
            return Identifier(tok.value)
        if tok.type == "LPAREN":
            self.consume("LPAREN")
            expr = self.parse_expression()
            self.consume("RPAREN")
            return expr
        raise ParserError(
            f"Unexpected token {tok.type} at line {tok.line}, column {tok.column}"
        )

