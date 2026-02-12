#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
from pathlib import Path

# Professional Imports - Move all imports to the top so PyInstaller finds them
import lexer
from parser import Parser
from semantic import analyze
from ir import generate_ir
from codegen import generate_c_code
import nl_ast  # Moved to top
import symbols # Moved to top

def _print_tokens(tokens):
    print("=== TOKENS ===")
    for tok in tokens:
        print(f"{tok.type:10} {repr(tok.value):8}  (line {tok.line}, col {tok.column})")
    print()

def _print_ast(node, indent: int = 0):
    """Pretty-print the AST as a tree using nl_ast nodes."""
    pad = "  " * indent
    # Use the nl_ast module directly to avoid internal ImportErrors
    if isinstance(node, (nl_ast.Program, nl_ast.Block)):
        print(f"{pad}{'Program' if isinstance(node, nl_ast.Program) else 'Block'}")
        for stmt in node.statements:
            _print_ast(stmt, indent + 1)
    elif isinstance(node, (nl_ast.VarDeclaration, nl_ast.Assignment)):
        print(f"{pad}{type(node).__name__} {node.name.name}")
        _print_ast(node.expr, indent + 1)
    elif isinstance(node, nl_ast.PrintStatement):
        print(f"{pad}Print")
        _print_ast(node.expr, indent + 1)
    elif isinstance(node, nl_ast.Identifier):
        print(f"{pad}Identifier {node.name}")
    elif isinstance(node, nl_ast.NumberLiteral):
        print(f"{pad}NumberLiteral {node.value}")
    elif isinstance(node, nl_ast.BinaryOp):
        print(f"{pad}BinaryOp {node.op}")
        _print_ast(node.left, indent + 1)
        _print_ast(node.right, indent + 1)

def _print_symbols(symbol_table):
    print("=== SYMBOL TABLE (global scope) ===")
    # Safety check for symbol table objects
    if not hasattr(symbol_table, 'symbols'):
        print(symbol_table)
        return
    for name, sym in symbol_table.symbols.items():
        print(f"{name}: type={sym.type}, initialized={sym.initialized}")
    print()

def compile_source(source_path, **kwargs):
    src_path = Path(source_path).absolute() # Use absolute path for user reliability
    if not src_path.exists():
        print(f"Error: Source file not found at {src_path}")
        return

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
    sym_table = analyze(ast_program)
    if kwargs.get('dump_symbols'): _print_symbols(sym_table)

    # 4. IR Generation
    ir_program = generate_ir(ast_program)
    if kwargs.get('dump_ir'):
        print("=== IR ===")
        for instr in ir_program.instructions: print(instr)

    # 5. C Code Generation
    c_code = generate_c_code(ir_program)
    # Ensure build directory exists in the same folder as the input file
    build_dir = src_path.parent / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    
    c_out = build_dir / (src_path.stem + ".c")
    c_out.write_text(c_code, encoding="utf-8")
    print(f"C code written to: {c_out}")

    # 6. Compilation Check
    compiler_bin = shutil.which("gcc") or shutil.which("clang")
    if not compiler_bin:
        print("\n[!] ERROR: GCC compiler not found in system PATH.")
        print("Please install MinGW/GCC so nlc can build your program.")
        return 

    exe_path = build_dir / (src_path.stem + (".exe" if os.name == "nt" else ""))
    
    try:
        # Compile command
        subprocess.run([compiler_bin, str(c_out), "-o", str(exe_path)], check=True)
        print(f"Executable created: {exe_path}")
        
        # Run command
        print("\n--- Running Output ---")
        subprocess.run([str(exe_path)], shell=True)
        print("\n-----------------------")
        
    except Exception as e:
        print(f"\n[!] Compilation/Execution Error: {e}")

def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: nlc <file.nl> [--tokens] [--ast] [--ir] [--symbols]")
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