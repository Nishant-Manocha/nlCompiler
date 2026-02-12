# NL Compiler (nlc)

A lightweight, hand-written compiler for the NL language. This tool translates `.nl` source code into C, compiles it via GCC, and executes the resulting program automatically.

## 🚀 Features
* **Full Pipeline**: Lexer -> Parser -> IR -> CodeGen -> GCC.
* **Portable**: Run `nlc` from any folder on your computer.
* **Integrated**: Automatically runs your program after compilation.

---

A professional-grade compiler for the NL language featuring a full pipeline: Lexing → Parsing → Semantic Analysis → IR → C-Codegen → Execution.

## 🛠️ Debugging Intermediate Results

Use these flags to inspect how the compiler processes your code.

### Lexical Analysis (Tokens)
`nlc file.nl --tokens`
* **Purpose**: Shows how the source text is broken into atomic units.
* **Example Output**: `NUMBER 2 (line 1, col 7)`.

### Syntax and Semantics Analysis(AST)
`nlc file.nl --ast`
* **Purpose**: Checks variable validity and Visualizes the hierarchical tree structure of your code.
* **Structure**: `Program -> Print -> NumberLiteral`.

### IR
`nlc file.nl --symbols --ir`
* **Purpose**: shows the Intermediate Representation.

---

## 🚀 Installation & Usage

1. **Setup**: Run `install.bat` as Administrator to add `nlc` to your Windows PATH.
2. **Compile & Run**: Type `nlc file.nl` to generate C code, compile with GCC, and execute instantly.