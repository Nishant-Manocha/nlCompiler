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

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.tokens = self._tokenize(text)
        self.pos = 0

    def get_next_token(self):
        """Used by main.py to fetch tokens one by one"""
        if self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            self.pos += 1
            return token
        return Token("EOF", None, 0, 0)

    def _tokenize(self, text: str):
        """Your original logic moved inside the class"""
        tokens = []
        line = 1
        col = 1
        i = 0
        length = len(text)

        while i < length:
            ch = text[i]

            if ch in "\r\n":
                if ch == "\r" and i + 1 < length and text[i + 1] == "\n":
                    i += 1
                line += 1
                col = 1
                i += 1
                continue

            if ch in WHITESPACE:
                col += 1
                i += 1
                continue

            if ch == "/" and i + 1 < length and text[i + 1] == "/":
                j = i
                while j < length and text[j] not in "\r\n":
                    j += 1
                col += (j - i)
                i = j
                continue

            if ch in DIGITS:
                start_col = col
                start_i = i
                while i < length and text[i] in DIGITS:
                    i += 1
                    col += 1
                value_text = text[start_i:i]
                tokens.append(Token("NUMBER", int(value_text), line, start_col))
                continue

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
            char_map = {
                "+": "PLUS", "-": "MINUS", "*": "MUL", "/": "DIV",
                "=": "ASSIGN", ";": "SEMICOLON", "(": "LPAREN",
                ")": "RPAREN", "{": "LBRACE", "}": "RBRACE"
            }
            
            if ch in char_map:
                tokens.append(Token(char_map[ch], ch, line, col))
            else:
                raise SyntaxError(f"Unexpected character {ch!r} at line {line}, column {col}")

            i += 1
            col += 1

        tokens.append(Token("EOF", None, line, col))
        return tokens