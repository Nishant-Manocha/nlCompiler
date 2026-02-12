# main.py

import sys
import os
import subprocess
from lexer import Lexer
from parser import Parser
from codegen import generate_c_code


def compile_file(filename, show_tokens=False):
    # -------- Check file existence --------
    if not os.path.isfile(filename):
        print(f"Error: File '{filename}' not found.")
        return

    # -------- Read source file --------
    with open(filename, "r") as f:
        source = f.read()

    # -------- LEXER --------
    lexer = Lexer(source)
    tokens = []

    while True:
        token = lexer.get_next_token()
        tokens.append(token)
        if token.type == "EOF":
            break

    # -------- Show tokens only --------
    if show_tokens:
        print("=== TOKENS ===")
        for token in tokens:
            print(token)
        return

    # -------- PARSER --------
    parser = Parser(tokens)
    ast = parser.parse()

    # -------- CODE GENERATION --------
    c_code = generate_c_code(ast)

    # Generate output names based on input filename
    base_name = os.path.splitext(os.path.basename(filename))[0]
    c_filename = base_name + ".c"
    exe_filename = base_name + ".exe"

    with open(c_filename, "w") as f:
        f.write(c_code)

    print(f"C code generated → {c_filename}")

    # -------- GCC COMPILATION --------
    result = subprocess.run(
        ["gcc", c_filename, "-o", exe_filename],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("Compilation failed:")
        print(result.stderr)
    else:
        print(f"Compilation successful → {exe_filename}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  nlc file.nl")
        print("  nlc file.nl --tokens")
        sys.exit(1)

    filename = sys.argv[1]
    show_tokens = "--tokens" in sys.argv

    compile_file(filename, show_tokens)


if __name__ == "__main__":
    main()
