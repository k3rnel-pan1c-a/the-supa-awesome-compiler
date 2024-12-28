from enum import Enum
from typing import Any


class TokenType(Enum):
    EOF = "EOF"
    ILLEGAL = "ILLEGAL"

    INT = "INT"
    FLOAT = "FLOAT"
    IDENTIFIER = "IDENTIFIER"

    PLUS = "PLUS"
    MINUS = "MINUS"
    SLASH = "SLASH"
    ASTERISK = "ASTERISK"
    MOD = "MOD"
    POW = "POW"

    BW_XOR = "BW_XOR"
    BW_OR = "BW_OR"
    BW_AND = "BW_AND"
    BW_NOT = "BW_NOT"

    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LCURLY = "LCURLY"
    RCURLY = "RCURLY"

    SEMICOLON = "SEMICOLON"
    COLON = "COLON"
    ARROW = "ARROW"

    # KEYWORDS
    LET = "LET"
    TYPE = "TYPE"
    FUNCTION = "FUNCTION"
    RETURN = "RETURN"
    IF = "IF"
    ELSE = "ELSE"
    TRUE = "TRUE"
    FALSE = "FALSE"

    EQUALS = "EQUALS"

    # CONDITIONALS
    EQ_EQ = "EQ_EQ"
    NOT_EQ = "NOT_EQ"
    LT_EQ = "LT_EQ"
    GT_EQ = "GT_EQ"
    GT = "GT"
    LT = "LT"
    NOT = "NOT"

    # LOOPS
    WHILE = "WHILE"
    FOR = "FOR"
    RANGE_SEPARATOR = "RANGE_SEPARATOR"

    # INCLUSION
    IN = "IN"


KEYWORDS: dict[str, TokenType] = {
    "let": TokenType.LET,
    "function": TokenType.FUNCTION,
    "return": TokenType.RETURN,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "in": TokenType.IN,
}

TYPE_KEYWORDS = ["int", "float", "bool"]


def lookup_identifier(identifier: str):
    token_type = KEYWORDS.get(identifier)
    if token_type is not None:
        return token_type

    elif identifier in TYPE_KEYWORDS:
        return TokenType.TYPE

    return TokenType.IDENTIFIER


class Token:
    def __init__(
        self, token_type: TokenType, token_literal: Any, token_position: tuple[int, int]
    ) -> None:
        self.token_type = token_type
        self.token_literal = token_literal
        self.token_position = token_position

    def __str__(self) -> str:
        return f"Token: {self.token_type}, Literal: {self.token_literal}, Position: {self.token_position}"
