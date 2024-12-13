from _token import TokenType, Token
from typing import Optional


class Lexer:
    def __init__(self, source: list[str]) -> None:
        self.__source = source

        self.__col: int = 0
        self.__row: int = 0

        self.__current_pos = (self.__row, self.__col)

        self.__current_char: Optional[str] = None

        self.__read_char()

    def __read_char(self) -> None:
        if self.__row >= len(self.__source):
            self.__current_char = None

        else:
            if self.__col >= len(self.__source[self.__row]):
                if self.__row != (len(self.__source) - 1):
                    self.__row += 1
                    self.__col = 0
                else:
                    self.__current_char = None

            else:
                self.__current_char = self.__source[self.__row][self.__col]
                self.__col += 1

            self.__current_pos = (self.__row, self.__col - 1)

    def __skip_whitespace(self) -> None:
        if self.__current_char in [" ", "\r", "\t"]:
            self.__read_char()

    @staticmethod
    def __is_digit(literal: str | None) -> bool:
        if literal is not None:
            return literal.isnumeric()
        else:
            return False

    @staticmethod
    def __new_token(
        token_type: TokenType, token_literal: str, pos: tuple[int, int]
    ) -> Token:
        return Token(token_type, token_literal, pos)

    def __peek_next_char(self) -> str:
        return self.__source[self.__row][self.__col]

    def __read_number(self) -> Token:
        start_pos = (self.__row, self.__col - 1)
        dot_count: int = 0
        number: str = ""

        while self.__is_digit(self.__current_char) or self.__current_char == ".":
            if self.__current_char == ".":
                dot_count += 1

            if dot_count > 1:
                return self.__new_token(
                    TokenType.ILLEGAL,
                    self.__source[self.__row][start_pos[1] : self.__col],
                    start_pos,
                )

            number += self.__current_char or ""
            self.__read_char()

            if self.__current_char is None:
                break

        if dot_count == 0:
            return self.__new_token(
                TokenType.INT,
                number,
                start_pos,
            )
        else:
            return self.__new_token(
                TokenType.FLOAT,
                number,
                start_pos,
            )

    def next_token(self) -> Token:
        self.__skip_whitespace()

        match self.__current_char:
            case "+":
                tok = self.__new_token(TokenType.PLUS, "+", self.__current_pos)
            case "-":
                tok = self.__new_token(TokenType.MINUS, "-", self.__current_pos)
            case "*":
                tok = self.__new_token(TokenType.ASTERISK, "*", self.__current_pos)
            case "/":
                tok = self.__new_token(TokenType.SLASH, "/", self.__current_pos)
            case "%":
                tok = self.__new_token(TokenType.MOD, "%", self.__current_pos)
            case "^":
                tok = self.__new_token(TokenType.XOR, "^", self.__current_pos)
            case "|":
                tok = self.__new_token(TokenType.OR, "|", self.__current_pos)
            case "&":
                tok = self.__new_token(TokenType.AND, "&", self.__current_pos)
            case "!":
                tok = self.__new_token(TokenType.NOT, "!", self.__current_pos)
            case "(":
                tok = self.__new_token(TokenType.LPAREN, "(", self.__current_pos)
            case ")":
                tok = self.__new_token(TokenType.RPAREN, ")", self.__current_pos)
            case ";":
                tok = self.__new_token(TokenType.SEMICOLON, ";", self.__current_pos)
            case None:
                tok = self.__new_token(
                    TokenType.EOF,
                    "EOF",
                    (self.__current_pos[0], self.__current_pos[1] + 1),
                )
            case _:
                if self.__is_digit(self.__current_char):
                    tok = self.__read_number()
                    return tok
                else:
                    tok = self.__new_token(
                        TokenType.ILLEGAL, self.__current_char, self.__current_pos
                    )

        self.__read_char()
        return tok
