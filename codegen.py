"""
codegen.py

Responsible for turning a simple IR into C code.
"""

from typing import Any
import ir  # Top-level import is safer for PyInstaller

def _format_ir_value(value: Any, op_map: dict) -> str:
    """
    Turn an IR value into a C expression string.
    """
    # Binary operation encoded as (op, left, right)
    if isinstance(value, tuple) and len(value) == 3:
        op, left, right = value
        if op not in op_map:
            raise ValueError(f"Unknown IR operator: {op!r}")
        left_s = _format_ir_value(left, op_map)
        right_s = _format_ir_value(right, op_map)
        return f"({left_s} {op_map[op]} {right_s})"

    # Simple literal / variable / temporary
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return value

    raise TypeError(f"Unsupported IR value: {value!r}")


def generate_c_code(ir_program: Any) -> str:
    """
    Generate C code from an IRProgram instance.
    """
    # Safety check: Ensure we actually received an IR object with instructions
    if not hasattr(ir_program, 'instructions'):
        raise AttributeError("Codegen Error: Expected IR object with 'instructions' attribute. " 
                             "Make sure main.py is calling ir.generate_ir(ast) first.")

    op_map = {
        "PLUS": "+",
        "MINUS": "-",
        "MUL": "*",
        "DIV": "/",
    }

    c_lines: list[str] = [
        "#include <stdio.h>",
        "",
        "int main() {",
    ]

    # Collect all variable / temporary names that need declarations
    vars_set = set()
    for instr in ir_program.instructions:
        if isinstance(instr, ir.IRAssign):
            vars_set.add(instr.target)
        elif isinstance(instr, ir.IRIfGoto):
            if isinstance(instr.cond, str):
                vars_set.add(instr.cond)

    # Declare all variables
    if vars_set:
        ordered = ", ".join(sorted(vars_set))
        c_lines.append(f"    int {ordered};")

    # Emit statements
    for instr in ir_program.instructions:
        if isinstance(instr, ir.IRAssign):
            expr_s = _format_ir_value(instr.value, op_map)
            c_lines.append(f"    {instr.target} = {expr_s};")
        elif isinstance(instr, ir.IRPrint):
            expr_s = _format_ir_value(instr.value, op_map)
            c_lines.append(f'    printf("%d\\n", {expr_s});')
        elif isinstance(instr, ir.IRLabel):
            c_lines.append(f"{instr.name}: ;")
        elif isinstance(instr, ir.IRGoto):
            c_lines.append(f"    goto {instr.label};")
        elif isinstance(instr, ir.IRIfGoto):
            expr_s = _format_ir_value(instr.cond, op_map)
            c_lines.append(f"    if ({expr_s}) goto {instr.label};")

    c_lines.append("    return 0;")
    c_lines.append("}")

    return "\n".join(c_lines)