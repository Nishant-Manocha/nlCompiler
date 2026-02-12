# NL Compiler (nlc)

A lightweight, hand-written compiler for the NL language. This tool translates `.nl` source code into C, compiles it via GCC, and executes the resulting program automatically.

## 🚀 Features
* **Full Pipeline**: Lexer -> Parser -> IR -> CodeGen -> GCC.
* **Portable**: Run `nlc` from any folder on your computer.
* **Integrated**: Automatically runs your program after compilation.

---

## 🛠️ Installation (One-Time Setup)

To use the `nlc` command anywhere on your Windows machine without typing long paths:

1. **Download** this repository to a folder (e.g., `C:\NLCompiler`).
2. **Right-click `install.bat`** and select **Run as Administrator**.
3. **Restart** your terminal or VS Code to apply the changes.

*This script adds the compiler to your Windows PATH so you don't have to use `.\` or activation scripts.*

---

## 💻 How to Use

You can now create an `.nl` file **anywhere** on your computer and run it.

1. Create a file named `hello.nl`:
   ```nl
   let x = 10;
   print(x + 5);