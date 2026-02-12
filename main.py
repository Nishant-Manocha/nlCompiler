import sys
import os
import subprocess

# Robust imports for PyInstaller bundling
try:
    import lexer
    import parser
    import ir       # <--- Added IR module
    import codegen
except ImportError as e:
    print(f"Internal Error: Missing compiler components. {e}")
    sys.exit(1)

def compile_file(filename, show_tokens=False):
    # -------- 1. Validate Input --------
    if not os.path.isfile(filename):
        print(f"Error: File '{filename}' not found.")
        return

    # -------- 2. Read Source --------
    try:
        with open(filename, "r") as f:
            source = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # -------- 3. Lexical Analysis (LEXER) --------
    _lexer = lexer.Lexer(source)
    tokens = []
    while True:
        token = _lexer.get_next_token()
        tokens.append(token)
        if token.type == "EOF":
            break

    if show_tokens:
        print("=== TOKENS ===")
        for token in tokens:
            print(token)
        return

    # -------- 4. Syntax Analysis (PARSER) --------
    _parser = parser.Parser(tokens)
    ast = _parser.parse()

    # -------- 5. IR Generation (The Missing Link) --------
    try:
        ir_program = ir.generate_ir(ast) 
    except Exception as e:
        print(f"IR Generation Error: {e}")
        return

    # -------- 6. Code Generation --------
    c_code = codegen.generate_c_code(ir_program)

    base_name = os.path.splitext(os.path.basename(filename))[0]
    c_filename = base_name + ".c"
    exe_filename = base_name + ".exe"

    try:
        with open(c_filename, "w") as f:
            f.write(c_code)
        print(f"C code generated → {c_filename}")
    except Exception as e:
        print(f"Error writing C file: {e}")
        return

    # -------- 7. GCC Compilation & Automatic Execution --------
    try:
        result = subprocess.run(
            ["gcc", c_filename, "-o", exe_filename],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("Compilation failed (GCC Error):")
            print(result.stderr)
        else:
            print(f"Compilation successful → {exe_filename}")
            
            # --- NEW: AUTO-RUN LOGIC ---
            print("\n--- Running Output ---")
            # We use shell=True to handle the .exe execution properly on Windows
            subprocess.run([f".\\{exe_filename}"], shell=True)
            print("-----------------------")
            # ---------------------------

    except FileNotFoundError:
        print("Error: 'gcc' not found. Please ensure MinGW/GCC is installed.")

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