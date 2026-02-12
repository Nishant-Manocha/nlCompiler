#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
from pathlib import Path

# Professional Imports
import lexer
from parser import Parser
from semantic import analyze
from ir import generate_ir
from codegen import generate_c_code

def _print_tokens(tokens):
    print("=== TOKENS ===")
    for tok in tokens:
        print(f"{tok.type:10} {repr(tok.value):8}  (line {tok.line}, col {tok.column})")
    print()

def _print_ast(node, indent: int = 0):
    """Pretty-print the AST as a tree."""
    from nl_ast import (
        Program, VarDeclaration, Assignment, PrintStatement,
        Identifier, NumberLiteral, BinaryOp, Block,
        IfStatement, WhileStatement,
    )
    pad = "  " * indent
    if isinstance(node, (Program, Block)):
        print(f"{pad}{'Program' if isinstance(node, Program) else 'Block'}")
        for stmt in node.statements:
            _print_ast(stmt, indent + 1)
    elif isinstance(node, (VarDeclaration, Assignment)):
        print(f"{pad}{type(node).__name__} {node.name.name}")
        _print_ast(node.expr, indent + 1)
    elif isinstance(node, PrintStatement):
        print(f"{pad}Print")
        _print_ast(node.expr, indent + 1)
    elif isinstance(node, Identifier):
        print(f"{pad}Identifier {node.name}")
    elif isinstance(node, NumberLiteral):
        print(f"{pad}NumberLiteral {node.value}")
    elif isinstance(node, BinaryOp):
        print(f"{pad}BinaryOp {node.op}")
        _print_ast(node.left, indent + 1)
        _print_ast(node.right, indent + 1)
    elif isinstance(node, IfStatement):
        print(f"{pad}If")
        _print_ast(node.condition, indent + 1)
        _print_ast(node.then_block, indent + 1)
        if getattr(node, "else_block", None):
            print(f"{pad}else")
            _print_ast(node.else_block, indent + 1)
    elif isinstance(node, WhileStatement):
        print(f"{pad}While")
        _print_ast(node.condition, indent + 1)
        _print_ast(node.body, indent + 1)

def _print_ir(ir_program):
    print("=== IR ===")
    for instr in ir_program.instructions:
        print(instr)
    print()

def _print_symbols(symbol_table):
    from symbols import SymbolTable
    print("=== SYMBOL TABLE (global scope) ===")
    if not isinstance(symbol_table, SymbolTable):
        print(symbol_table)
        return
    for name, sym in symbol_table.symbols.items():
        print(f"{name}: type={sym.type}, initialized={sym.initialized}")
    print()

def compile_source(source_path, **kwargs):
    src_path = Path(source_path)
    if not src_path.exists():
        raise FileNotFoundError(f"Source file not found: {src_path}")

    text = src_path.read_text(encoding="utf-8")

    # 1. Lexing
    _lexer = lexer.Lexer(text)
    tokens = []
    while True:
        token = _lexer.get_next_token()
        tokens.append(token)
        if token.type == "EOF": break
    if kwargs.get('dump_tokens'): _print_tokens(tokens)

    # 2. Parsing
    parser_obj = Parser(tokens)
    ast_program = parser_obj.parse()
    if kwargs.get('dump_ast'):
        print("=== AST ==="); _print_ast(ast_program); print()

    # 3. Semantic Analysis
    symbols = analyze(ast_program)
    if kwargs.get('dump_symbols'): _print_symbols(symbols)

    # 4. IR Generation
    ir_program = generate_ir(ast_program)
    if kwargs.get('dump_ir'): _print_ir(ir_program)

    # 5. C Code Generation
    c_code = generate_c_code(ir_program)
    build_dir = src_path.parent / "build"
    build_dir.mkdir(exist_ok=True)
    c_out = build_dir / (src_path.stem + ".c")
    c_out.write_text(c_code, encoding="utf-8")
    print(f"C code written to: {c_out}")

    # 6. Compilation (FIXED for End-Users)
    compiler_bin = shutil.which("gcc") or shutil.which("clang")
    
    if not compiler_bin:
        print("\n[!] ERROR: C compiler (gcc) not found.")
        print("To run .nl files, please install MinGW/GCC and add it to your PATH.")
        return 

    exe_path = build_dir / (src_path.stem + (".exe" if os.name == "nt" else ""))
    cmd = [compiler_bin, str(c_out), "-o", str(exe_path)]
    
    try:
        # Run GCC to compile
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Executable created: {exe_path}")
            # AUTO-RUN LOGIC
            if exe_path.exists():
                print("\n--- Running Output ---")
                subprocess.run([str(exe_path)], shell=True)
                print("\n-----------------------")
        
    except FileNotFoundError:
        print("\n[!] Error: The system could not find the compiler executable.")
    except subprocess.CalledProcessError as e:
        print("\n[!] GCC Compilation Error:")
        print(e.stderr)

def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python compiler.py <file.nl> [--tokens] [--ast] [--ir] [--symbols]")
        return
    
    compile_source(
        args[0],
        dump_tokens="--tokens" in args,
        dump_ast="--ast" in args,
        dump_ir="--ir" in args,
        dump_symbols="--symbols" in args
    )

if __name__ == "__main__":
    main()