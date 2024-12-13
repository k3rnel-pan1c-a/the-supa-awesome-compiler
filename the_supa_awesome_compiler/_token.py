from enum import Enum
from typing import Any


class TokenType(Enum):
    EOF = "EOF"
    ILLEGAL = "ILLEGAL"

    INT = "INT"
    FLOAT = "FLOAT"

    PLUS = "PLUS"
    MINUS = "MINUS"
    SLASH = "SLASH"
    ASTERISK = "ASTERISK"
    MOD = "%"

    XOR = "XOR"
    OR = "OR"
    AND = "AND"
    NOT = "NOT"

    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LCURLY = "LCURLY"
    RCURLY = "RCURLY"

    SEMICOLON = "SEMICOLON"


class Token:
    def __init__(
        self, token_type: TokenType, token_literal: Any, token_position: tuple[int, int]
    ) -> None:
        self.token_type = token_type
        self.token_literal = token_literal
        self.token_position = token_position

    def __str__(self) -> str:
        return f"Token: {self.token_type}, Literal: {self.token_literal}, Position: {self.token_position}"
