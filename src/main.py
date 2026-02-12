import sys
import os
import subprocess
import argparse  # <--- Use this for professional flag handling

# Your existing imports
try:
    import lexer
    import parser
    import ir
    import codegen
    # import semantic  # Uncomment if you have semantic.py ready
except ImportError as e:
    print(f"Internal Error: {e}")
    sys.exit(1)

def compile_file(filename, args):
    if not os.path.isfile(filename):
        print(f"Error: File '{filename}' not found.")
        return

    with open(filename, "r") as f:
        source = f.read()

    # 1. LEXER
    _lexer = lexer.Lexer(source)
    tokens = []
    while True:
        token = _lexer.get_next_token()
        tokens.append(token)
        if token.type == "EOF": break
    
    if args.tokens:
        print("\n=== TOKENS ===")
        for t in tokens: print(t)
        return # Stop here if user only wants tokens

    # 2. PARSER (AST)
    _parser = parser.Parser(tokens)
    ast = _parser.parse()
    if args.ast:
        print("\n=== ABSTRACT SYNTAX TREE (AST) ===")
        print(ast) # Make sure your AST classes have __str__ or __repr__
        return

    # 3. IR GENERATION
    ir_program = ir.generate_ir(ast)
    if args.ir:
        print("\n=== INTERMEDIATE REPRESENTATION (IR) ===")
        print(ir_program)
        return

    # 4. CODEGEN
    c_code = codegen.generate_c_code(ir_program)
    
    base_name = os.path.splitext(os.path.basename(filename))[0]
    c_filename = f"{base_name}.c"
    exe_filename = f"{base_name}.exe"

    with open(c_filename, "w") as f:
        f.write(c_code)

    # 5. GCC & RUN
    result = subprocess.run(["gcc", c_filename, "-o", exe_filename], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Successfully compiled: {exe_filename}")
        print("\n--- Running Output ---")
        subprocess.run([f".\\{exe_filename}"], shell=True)
    else:
        print("GCC Error:", result.stderr)

def main():
    arg_parser = argparse.ArgumentParser(description="NL Compiler (nlc)")
    arg_parser.add_argument("filename", help="The .nl file to compile")
    arg_parser.add_argument("--tokens", action="store_true", help="Show tokens and stop")
    arg_parser.add_argument("--ast", action="store_true", help="Show AST and stop")
    arg_parser.add_argument("--ir", action="store_true", help="Show IR and stop")
    arg_parser.add_argument("--symbols", action="store_true", help="Show Symbol Table")

    args = arg_parser.parse_args()
    compile_file(args.filename, args)

if __name__ == "__main__":
    main()