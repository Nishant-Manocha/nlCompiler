"""
codegen.py

Responsible for turning a simple IR into C code.
"""

from typing import Any, Iterable


def _format_ir_value(value: Any, op_map: dict) -> str:
    """
    Turn an IR value into a C expression string.

    value can be:
      - int                      -> numeric literal
      - str                      -> variable / temporary name
      - (op, left, right) tuple  -> binary operation
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

    The IR is expected to come from ir.generate_ir and contain instructions:
      - IRAssign(target: str, value: int | str | (op, left, right))
      - IRPrint(value: int | str | (op, left, right))
      - IRLabel(name: str)
      - IRGoto(label: str)
      - IRIfGoto(cond: int | str | (op, left, right), label: str)
    """
    from ir import IRAssign, IRPrint, IRLabel, IRGoto, IRIfGoto  # local import to avoid circular deps

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
        if isinstance(instr, IRAssign):
            vars_set.add(instr.target)
        elif isinstance(instr, IRIfGoto):
            # condition may be a temp or variable name
            if isinstance(instr.cond, str):
                vars_set.add(instr.cond)

    # Declare all variables (including temporaries like t1, t2, ...)
    if vars_set:
        ordered = ", ".join(sorted(vars_set))
        c_lines.append(f"    int {ordered};")

    # Emit statements
    for instr in ir_program.instructions:
        if isinstance(instr, IRAssign):
            expr_s = _format_ir_value(instr.value, op_map)
            c_lines.append(f"    {instr.target} = {expr_s};")
        elif isinstance(instr, IRPrint):
            expr_s = _format_ir_value(instr.value, op_map)
            c_lines.append(f'    printf("%d\\n", {expr_s});')
        elif isinstance(instr, IRLabel):
            # Labels appear at column 0 in C
            c_lines.append(f"{instr.name}: ;")
        elif isinstance(instr, IRGoto):
            c_lines.append(f"    goto {instr.label};")
        elif isinstance(instr, IRIfGoto):
            expr_s = _format_ir_value(instr.cond, op_map)
            c_lines.append(f"    if ({expr_s}) goto {instr.label};")
        else:
            raise ValueError(f"Unknown IR instruction: {instr!r}")

    c_lines.append("    return 0;")
    c_lines.append("}")

    return "\n".join(c_lines)
