from _token import TokenType, Token, lookup_identifier
from typing import Optional
from collections import deque


class Lexer:
    def __init__(self, source: list[str]) -> None:
        self.__source = source

        self.__col: int = 0
        self.__row: int = 0

        self.__current_pos = (self.__row, self.__col)

        self.current_char: Optional[str] = None

        self.__read_char()

        self.__token_queue = deque()

    @property
    def current_token(self):
        return self.current_char

    def __read_char(self) -> None:
        if self.__row >= len(self.__source):
            self.current_char = None

        else:
            if self.__col >= len(self.__source[self.__row]):
                if self.__row != (len(self.__source) - 1):
                    self.__row += 1
                    self.__col = 1
                    self.current_char = self.__source[self.__row][self.__col - 1]
                else:
                    self.current_char = None

            else:
                self.current_char = self.__source[self.__row][self.__col]
                self.__col += 1

            self.__current_pos = (self.__row, self.__col - 1)

    def __skip_whitespace(self) -> None:
        while self.current_char in [" ", "\r", "\t", "\n"]:
            self.__read_char()

    @staticmethod
    def __is_digit(literal: str | None) -> bool:
        if literal is not None:
            return literal.isnumeric()
        return False

    @staticmethod
    def __is_letter(literal: str | None) -> bool:
        if literal is not None:
            return literal.isalpha() or literal == "_"
        return False

    @staticmethod
    def is_digit(char: str):
        return char.isnumeric()

    @staticmethod
    def pop_while_not_empty(stack):
        while len(stack):
            yield stack.pop()

    @staticmethod
    def __new_token(
        token_type: TokenType, token_literal: str, pos: tuple[int, int]
    ) -> Token:
        return Token(token_type, token_literal, pos)

    def __peek_next_char(self) -> str:
        return self.__source[self.__row][self.__col]

    def __read_literal(self):
        literal: str = ""

        while self.current_char is not None and self.__is_letter(self.current_char):
            literal += self.current_char
            self.__read_char()

        return literal

    def __read_num_or_range(self):
        current_pos = (self.__row, self.__col - 1)
        char_count = 0
        dot_count: int = 0
        literal = ""

        while self.__is_digit(self.current_char) or self.current_char == ".":
            if self.current_char == ".":
                dot_count += 1

            literal += self.current_char

            self.__read_char()

        if dot_count > 2:
            return self.__new_token(
                TokenType.ILLEGAL,
                self.__source[self.__row][current_pos[0] : current_pos[0] + char_count],
                current_pos,
            )

        elif dot_count == 2:
            de = deque(literal)
            range_start = ""
            range_end_reversed = []

            while self.__is_digit(de[0]):
                range_start += de.popleft()
            while self.__is_digit(de[-1]):
                range_end_reversed.append(de.pop())

            if not len(range_end_reversed):
                return self.__new_token(
                    TokenType.ILLEGAL,
                    self.__source[self.__row][
                        current_pos[0] : current_pos[0] + char_count
                    ],
                    current_pos,
                )

            elif de[0] != de[-1] != "." or len(de) != 2:
                return self.__new_token(
                    TokenType.ILLEGAL,
                    self.__source[self.__row][
                        current_pos[0] : current_pos[0] + char_count
                    ],
                    current_pos,
                )

            else:
                range_end = "".join(self.pop_while_not_empty(range_end_reversed))
                self.__token_queue.append(
                    self.__new_token(TokenType.RANGE_SEPARATOR, "..", current_pos)
                )
                self.__token_queue.append(
                    self.__new_token(TokenType.INT, range_end, current_pos)
                )

                return self.__new_token(TokenType.INT, range_start, current_pos)

        elif dot_count == 1:
            return self.__new_token(
                TokenType.FLOAT,
                literal,
                current_pos,
            )

        else:
            return self.__new_token(
                TokenType.INT,
                literal,
                current_pos,
            )

    # def __read_number(self) -> Token:
    #     start_pos = (self.__row, self.__col - 1)
    #     dot_count: int = 0
    #     number: str = ""
    #
    #     while self.__is_digit(self.current_char) or self.current_char == ".":
    #         if self.current_char == ".":
    #             dot_count += 1
    #
    #         if dot_count > 1:
    #             return self.__new_token(
    #                 TokenType.ILLEGAL,
    #                 self.__source[self.__row][start_pos[1] : self.__col],
    #                 start_pos,
    #             )
    #
    #         number += self.current_char or ""
    #         self.__read_char()
    #
    #         if self.current_char is None:
    #             break
    #
    #     if dot_count == 0:
    #         return self.__new_token(
    #             TokenType.INT,
    #             number,
    #             start_pos,
    #         )
    #     else:
    #         return self.__new_token(
    #             TokenType.FLOAT,
    #             number,
    #             start_pos,
    #         )

    def next_token(self) -> Token:
        self.__skip_whitespace()

        if self.__token_queue:
            return self.__token_queue.popleft()

        match self.current_char:
            case "+":
                tok = self.__new_token(TokenType.PLUS, "+", self.__current_pos)
            case "-":
                if self.__peek_next_char() == ">":
                    tok = self.__new_token(TokenType.ARROW, "->", self.__current_pos)
                    self.__read_char()
                else:
                    tok = self.__new_token(TokenType.MINUS, "-", self.__current_pos)
            case "*":
                tok = self.__new_token(TokenType.ASTERISK, "*", self.__current_pos)
            case "/":
                tok = self.__new_token(TokenType.SLASH, "/", self.__current_pos)
            case "%":
                tok = self.__new_token(TokenType.MOD, "%", self.__current_pos)
            case "^":
                tok = self.__new_token(TokenType.BW_XOR, "^", self.__current_pos)
            case "|":
                tok = self.__new_token(TokenType.BW_OR, "|", self.__current_pos)
            case "&":
                tok = self.__new_token(TokenType.BW_AND, "&", self.__current_pos)
            case "~":
                tok = self.__new_token(TokenType.BW_NOT, "~", self.__current_pos)
            case "!":
                if self.__peek_next_char() == "=":
                    tok = self.__new_token(TokenType.NOT_EQ, "!=", self.__current_pos)
                    self.__read_char()
                else:
                    tok = self.__new_token(TokenType.NOT, "!", self.__current_pos)
            case "(":
                tok = self.__new_token(TokenType.LPAREN, "(", self.__current_pos)
            case ")":
                tok = self.__new_token(TokenType.RPAREN, ")", self.__current_pos)
            case "{":
                tok = self.__new_token(TokenType.LCURLY, "{", self.__current_pos)
            case "}":
                tok = self.__new_token(TokenType.RCURLY, "}", self.__current_pos)
            case "[":
                tok = self.__new_token(TokenType.LSQR, "[", self.__current_pos)
            case "]":
                tok = self.__new_token(TokenType.RSQR, "]", self.__current_pos)
            case ";":
                tok = self.__new_token(TokenType.SEMICOLON, ";", self.__current_pos)
            case ":":
                tok = self.__new_token(TokenType.COLON, ":", self.__current_pos)
            case ",":
                tok = self.__new_token(TokenType.COMMA, ",", self.__current_pos)
            case "=":
                if self.__peek_next_char() == "=":
                    tok = self.__new_token(TokenType.EQ_EQ, "==", self.__current_pos)
                    self.__read_char()
                else:
                    tok = self.__new_token(TokenType.EQUALS, "=", self.__current_pos)
            case ">":
                if self.__peek_next_char() == "=":
                    tok = self.__new_token(TokenType.GT_EQ, ">=", self.__current_pos)
                    self.__read_char()
                else:
                    tok = self.__new_token(TokenType.GT, ">", self.__current_pos)

            case "<":
                if self.__peek_next_char() == "=":
                    tok = self.__new_token(TokenType.LT_EQ, "<=", self.__current_pos)
                    self.__read_char()
                else:
                    tok = self.__new_token(TokenType.LT, "<", self.__current_pos)

            case None:
                tok = self.__new_token(
                    TokenType.EOF,
                    "EOF",
                    (self.__current_pos[0], self.__current_pos[1] + 1),
                )
            case _:
                if self.__is_letter(self.current_char):
                    literal = self.__read_literal()
                    literal_type = lookup_identifier(literal)
                    # if literal_type in TYPE_KEYWORDS:
                    #     self.__read_array_type()
                    tok = self.__new_token(literal_type, literal, self.__current_pos)
                    return tok
                if self.__is_digit(self.current_char):
                    tok = self.__read_num_or_range()
                    return tok
                else:
                    tok = self.__new_token(
                        TokenType.ILLEGAL, self.current_char, self.__current_pos
                    )

        self.__read_char()
        return tok
