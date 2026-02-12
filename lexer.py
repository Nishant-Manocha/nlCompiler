"""
lexer.py

Simple hand-written lexical analyzer for NL source code.
Converts source text into a list of tokens.
"""

from dataclasses import dataclass


@dataclass
class Token:
    type: str
    value: object
    line: int
    column: int


KEYWORDS = {
    "let": "LET",
    "print": "PRINT",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
}

WHITESPACE = " \t"
DIGITS = "0123456789"
IDENT_START = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
IDENT_PART = IDENT_START + DIGITS


def tokenize(text: str):
    tokens = []
    line = 1
    col = 1
    i = 0
    length = len(text)

    while i < length:
        ch = text[i]

        # Newlines (handle Windows \r\n too)
        if ch in "\r\n":
            if ch == "\r" and i + 1 < length and text[i + 1] == "\n":
                i += 1
            line += 1
            col = 1
            i += 1
            continue

        # Whitespace
        if ch in WHITESPACE:
            col += 1
            i += 1
            continue

        # Line comments starting with //
        if ch == "/" and i + 1 < length and text[i + 1] == "/":
            # Skip until end of line, updating column
            j = i
            while j < length and text[j] not in "\r\n":
                j += 1
            col += (j - i)
            i = j
            continue

        # Numbers
        if ch in DIGITS:
            start_col = col
            start_i = i
            while i < length and text[i] in DIGITS:
                i += 1
                col += 1
            value_text = text[start_i:i]
            tokens.append(Token("NUMBER", int(value_text), line, start_col))
            continue

        # Identifiers / keywords
        if ch in IDENT_START:
            start_col = col
            start_i = i
            while i < length and text[i] in IDENT_PART:
                i += 1
                col += 1
            ident = text[start_i:i]
            token_type = KEYWORDS.get(ident, "IDENT")
            tokens.append(Token(token_type, ident, line, start_col))
            continue

        # Single-character tokens
        if ch == "+":
            tokens.append(Token("PLUS", ch, line, col))
        elif ch == "-":
            tokens.append(Token("MINUS", ch, line, col))
        elif ch == "*":
            tokens.append(Token("MUL", ch, line, col))
        elif ch == "/":
            tokens.append(Token("DIV", ch, line, col))
        elif ch == "=":
            tokens.append(Token("ASSIGN", ch, line, col))
        elif ch == ";":
            tokens.append(Token("SEMICOLON", ch, line, col))
        elif ch == "(":
            tokens.append(Token("LPAREN", ch, line, col))
        elif ch == ")":
            tokens.append(Token("RPAREN", ch, line, col))
        elif ch == "{":
            tokens.append(Token("LBRACE", ch, line, col))
        elif ch == "}":
            tokens.append(Token("RBRACE", ch, line, col))
        else:
            raise SyntaxError(f"Unexpected character {ch!r} at line {line}, column {col}")

        i += 1
        col += 1

    tokens.append(Token("EOF", None, line, col))
    return tokens

