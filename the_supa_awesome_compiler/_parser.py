from _lexer import Lexer
from _token import Token, TokenType
from typing import Callable, Optional, cast
from enum import Enum, auto

from _AST import Statement, Expression, Program
from _AST import ExpressionStatement
from _AST import InfixExpression
from _AST import IntegerLiteral, FloatLiteral


class PrecedenceType(Enum):
    P_LOWEST = 0
    P_EQUALS = auto()
    P_LESSGREATER = auto()
    P_SUM = auto()
    P_PRODUCT = auto()
    P_EXPONENT = auto()
    P_PREFIX = auto()
    P_CALL = auto()
    P_INDEX = auto()


PRECEDENCES: dict[TokenType, PrecedenceType] = {
    TokenType.PLUS: PrecedenceType.P_SUM,
    TokenType.MINUS: PrecedenceType.P_SUM,
    TokenType.SLASH: PrecedenceType.P_PRODUCT,
    TokenType.ASTERISK: PrecedenceType.P_PRODUCT,
    TokenType.MOD: PrecedenceType.P_PRODUCT,
}


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer

        self._errors: list[str] = []

        self.__current_token: Optional[Token] = None
        self.__peek_token: Optional[Token] = None

        self.__prefix_parse_fns: dict[TokenType, Callable[[], Expression | None]] = {
            TokenType.INT: self.__parse_int_literal,
            TokenType.FLOAT: self.__parse_float_literal,
            TokenType.LPAREN: self.__parse_grouped_expression,
        }
        self.__infix_parse_fns: dict[
            TokenType, Callable[[Expression], InfixExpression | None]
        ] = {
            TokenType.PLUS: self.__parse_infix_expression,
            TokenType.MINUS: self.__parse_infix_expression,
            TokenType.SLASH: self.__parse_infix_expression,
            TokenType.ASTERISK: self.__parse_infix_expression,
            TokenType.MOD: self.__parse_infix_expression,
        }

        self.__next_token()
        self.__next_token()

    def __next_token(self) -> None:
        self.__current_token = self.__peek_token
        self.__peek_token = self.lexer.next_token()

    def __peak_token_is(self, token_type: TokenType) -> bool:
        return cast(Token, self.__peek_token).token_type is token_type

    def __expect_token(self, token_type: TokenType) -> bool:
        if self.__peak_token_is(token_type):
            self.__next_token()
            return True
        else:
            self.__peek_error(token_type)
            return False

    def __peek_error(self, token_type: TokenType) -> None:
        self._errors.append(
            f"Expected next token to be: {token_type}, got {cast(Token, self.__peek_token).token_type} instead."
        )

    def __no_prefix_parse_fn_error(self, token_type: TokenType) -> None:
        self._errors.append(f"No prefix parse function found for {token_type}")

    def __current_precedence(self) -> PrecedenceType:
        precedence: PrecedenceType | None = PRECEDENCES.get(
            cast(Token, self.__current_token).token_type
        )
        if precedence is None:
            return PrecedenceType.P_LOWEST
        return precedence

    def __peak_precedence(self) -> PrecedenceType:
        precedence: PrecedenceType | None = PRECEDENCES.get(
            cast(Token, self.__peek_token).token_type
        )
        if precedence is None:
            return PrecedenceType.P_LOWEST
        return precedence

    def parse_program(self) -> Program:
        program: Program = Program()

        while cast(Token, self.__current_token).token_type != TokenType.EOF:
            statement: Statement = self.__parse_statement()

            if statement is not None:
                program.statements.append(statement)

            self.__next_token()

        return program

    def __parse_statement(self) -> Statement:
        return self.__parse_expression_statement()

    def __parse_expression(self, precedence: PrecedenceType) -> Expression | None:
        prefix_fn: Callable | None = self.__prefix_parse_fns.get(
            cast(Token, self.__current_token).token_type
        )
        if prefix_fn is None:
            self.__no_prefix_parse_fn_error(
                cast(Token, self.__current_token).token_type
            )
            return None

        left_expression = prefix_fn()
        while (
            not self.__peak_token_is(TokenType.SEMICOLON)
            and precedence.value < self.__peak_precedence().value
        ):
            infix_fn: Callable | None = self.__infix_parse_fns.get(
                cast(Token, self.__peek_token).token_type
            )
            if infix_fn is None:
                return left_expression

            self.__next_token()

            left_expression = infix_fn(left_expression)

        return left_expression

    def __parse_expression_statement(self) -> ExpressionStatement:
        expression = self.__parse_expression(PrecedenceType.P_LOWEST)

        if self.__peak_token_is(TokenType.SEMICOLON):
            self.__next_token()

        statement: ExpressionStatement = ExpressionStatement(expression)

        return statement

    def __parse_infix_expression(self, left_node: Expression) -> InfixExpression | None:
        infix_expression: InfixExpression = InfixExpression(
            left_node=left_node,
            operator=cast(Token, self.__current_token).token_literal,
            right_node=Optional[Expression],
        )
        precedence = self.__current_precedence()

        self.__next_token()

        if not (right_node := self.__parse_expression(precedence)):
            self._errors.append(
                f"Could not parse the expression with the left node: {left_node}"
            )
            return None

        infix_expression.right_node = right_node

        return infix_expression

    def __parse_grouped_expression(self):
        self.__next_token()

        expression: Expression = self.__parse_expression(PrecedenceType.P_LOWEST)

        if not self.__peek_error(TokenType.RPAREN):
            return None

        return expression

    def __parse_int_literal(self) -> Expression | None:
        int_literal: IntegerLiteral = IntegerLiteral()

        try:
            int_literal.int_literal = int(
                cast(Token, self.__current_token).token_literal
            )
            return int_literal
        except ValueError:
            self._errors.append(
                f"Could not parse {cast(Token, self.__current_token).token_literal} as an int"
            )
            return None

    def __parse_float_literal(self) -> Expression | None:
        float_literal: FloatLiteral = FloatLiteral()
        try:
            float_literal.float_literal = float(
                cast(Token, self.__current_token).token_literal
            )
            return float_literal
        except ValueError:
            self._errors.append(
                f"Could not parse {cast(Token, self.__current_token).token_literal} as a float"
            )
            return None
