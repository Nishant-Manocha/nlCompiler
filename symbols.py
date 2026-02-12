"""
symbols.py

Symbol table and symbol representation for semantic analysis.
"""

from dataclasses import dataclass


@dataclass
class Symbol:
    name: str
    type: str = "int"
    initialized: bool = False


class SymbolTable:
    """
    Simple hierarchical symbol table (supports nested scopes via parent).
    """

    def __init__(self, parent=None):
        self.parent = parent
        self.symbols = {}

    def define(self, name: str, sym_type: str = "int") -> Symbol:
        if name in self.symbols:
            raise RuntimeError(f"Variable '{name}' already defined in this scope")
        sym = Symbol(name=name, type=sym_type)
        self.symbols[name] = sym
        return sym

    def lookup(self, name: str) -> Symbol:
        if name in self.symbols:
            return self.symbols[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        raise RuntimeError(f"Undefined variable '{name}'")

    def assign(self, name: str) -> Symbol:
        sym = self.lookup(name)
        sym.initialized = True
        return sym

