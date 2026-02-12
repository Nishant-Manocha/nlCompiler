# ast_nodes.py

class NumberNode:
    def __init__(self, value):
        self.value = value

class BinOpNode:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class PrintNode:
    def __init__(self, expression):
        self.expression = expression
