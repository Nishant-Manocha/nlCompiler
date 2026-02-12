"""
compiler.py

End-to-end driver for the NL compiler:
  - reads a .nl source file
  - runs lexical analysis (lexer)
  - parses into an AST (parser)
  - performs semantic analysis (semantic)
  - generates IR (ir)
  - generates C code (codegen)
  - optionally invokes a C compiler to produce an executable
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

from lexer import tokenize
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

    pad = "  " * indent

    if isinstance(node, Program):
        print(f"{pad}Program")
        for stmt in node.statements:
            _print_ast(stmt, indent + 1)
    elif isinstance(node, Block):
        print(f"{pad}Block")
        for stmt in node.statements:
            _print_ast(stmt, indent + 1)
    elif isinstance(node, VarDeclaration):
        print(f"{pad}VarDeclaration {node.name.name}")
        _print_ast(node.expr, indent + 1)
    elif isinstance(node, Assignment):
        print(f"{pad}Assignment {node.name.name}")
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
        if getattr(node, "else_block", None) is not None:
            print(f"{pad}else")
            _print_ast(node.else_block, indent + 1)
    elif isinstance(node, WhileStatement):
        print(f"{pad}While")
        _print_ast(node.condition, indent + 1)
        _print_ast(node.body, indent + 1)
    else:
        print(f"{pad}{type(node).__name__}: {node!r}")


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


def compile_source(
    source_path: str,
    *,
    output_exe: str | None = None,
    dump_tokens: bool = False,
    dump_ast: bool = False,
    dump_ir: bool = False,
    dump_symbols: bool = False,
    no_exe: bool = False,
):
    """
    Compile an NL source file to C and, if possible, to an executable.

    Optional debug outputs:
      - dump_tokens: print tokens from the lexer
      - dump_ast:    print the parsed AST tree
      - dump_ir:     print the intermediate representation
      - dump_symbols:print the symbol table after semantic analysis
      - no_exe:      stop after generating C (do not call gcc/clang)
    """
    src_path = Path(source_path)
    if not src_path.exists():
        raise FileNotFoundError(f"Source file not found: {src_path}")

    text = src_path.read_text(encoding="utf-8")

    # 1. Lexing
    tokens = tokenize(text)
    if dump_tokens:
        _print_tokens(tokens)

    # 2. Parsing
    parser = Parser(tokens)
    ast_program = parser.parse()
    if dump_ast:
        print("=== AST ===")
        _print_ast(ast_program)
        print()

    # 3. Semantic analysis (build/check symbol table)
    symbols = analyze(ast_program)
    if dump_symbols:
        _print_symbols(symbols)

    # 4. IR generation
    ir_program = generate_ir(ast_program)
    if dump_ir:
        _print_ir(ir_program)

    # 5. C code generation
    c_code = generate_c_code(ir_program)

    build_dir = src_path.parent / "build"
    build_dir.mkdir(exist_ok=True)

    c_out = build_dir / (src_path.stem + ".c")
    c_out.write_text(c_code, encoding="utf-8")
    print(f"C code written to: {c_out}")

    if no_exe:
        # Caller only wants front-end / C output
        return

    # 6. Try to invoke a C compiler (gcc or clang)
    compiler = shutil.which("gcc") or shutil.which("clang")
    if compiler is None:
        print("No C compiler (gcc/clang) found on PATH.")
        print("You can compile the C file manually, for example:")
        print(f"  gcc {c_out} -o {build_dir / (src_path.stem + '.exe')}")
        return

    exe_name = output_exe or src_path.stem
    if os.name == "nt" and not exe_name.lower().endswith(".exe"):
        exe_name += ".exe"
    exe_path = build_dir / exe_name

    cmd = [compiler, str(c_out), "-o", str(exe_path)]
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise RuntimeError("C compiler failed")

    print(f"Executable created at: {exe_path}")


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        print(
            "Usage: python compiler.py path/to/file.nl "
            "[--tokens] [--ast] [--ir] [--symbols] [--no-exe]"
        )
        raise SystemExit(1)

    source = argv[0]
    flags = set(argv[1:])

    compile_source(
        source,
        dump_tokens="--tokens" in flags,
        dump_ast="--ast" in flags or "--parse-tree" in flags,
        dump_ir="--ir" in flags,
        dump_symbols="--symbols" in flags,
        no_exe="--no-exe" in flags,
    )


if __name__ == "__main__":
    main()

