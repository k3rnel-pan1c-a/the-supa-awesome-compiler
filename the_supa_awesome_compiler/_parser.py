from _lexer import Lexer
from _token import Token, TokenType
from typing import Callable, Optional, cast
from enum import Enum, auto

from _AST import Statement, Expression, Program
from _AST import (
    ExpressionStatement,
    AssignmentStatement,
    ReturnStatement,
    BlockStatement,
    FunctionStatement,
    ReassignmentStatement,
    IfStatement,
    WhileLoop,
)
from _AST import InfixExpression, PrefixExpression
from _AST import IntegerLiteral, FloatLiteral, IdentifierLiteral, BooleanLiteral


class PrecedenceType(Enum):
    P_LOWEST = 0
    P_EQUALS = auto()
    P_LESSGREATER = auto()
    P_BW_OR = auto()
    P_BW_XOR = auto()
    P_BW_AND = auto()
    P_BW_NOT = auto()
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
    TokenType.EQ_EQ: PrecedenceType.P_EQUALS,
    TokenType.NOT_EQ: PrecedenceType.P_EQUALS,
    TokenType.GT: PrecedenceType.P_LESSGREATER,
    TokenType.LT: PrecedenceType.P_LESSGREATER,
    TokenType.GT_EQ: PrecedenceType.P_LESSGREATER,
    TokenType.LT_EQ: PrecedenceType.P_LESSGREATER,
    TokenType.BW_OR: PrecedenceType.P_BW_OR,
    TokenType.BW_XOR: PrecedenceType.P_BW_XOR,
    TokenType.BW_AND: PrecedenceType.P_BW_AND,
    TokenType.BW_NOT: PrecedenceType.P_BW_NOT,
}


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer

        self.errors: list[str] = []

        self.__current_token: Optional[Token] = None
        self.__peek_token: Optional[Token] = None

        self.__prefix_parse_fns: dict[TokenType, Callable[[], Expression | None]] = {
            TokenType.INT: self.__parse_int_literal,
            TokenType.FLOAT: self.__parse_float_literal,
            TokenType.LPAREN: self.__parse_grouped_expression,
            TokenType.IDENTIFIER: self.__parse_identifier_literal,
            TokenType.TRUE: self.__parse_boolean_literal,
            TokenType.FALSE: self.__parse_boolean_literal,
            TokenType.BW_NOT: self.__parse_bitwise_not_expression,
        }
        self.__infix_parse_fns: dict[
            TokenType, Callable[[Expression], InfixExpression | None]
        ] = {
            TokenType.PLUS: self.__parse_infix_expression,
            TokenType.MINUS: self.__parse_infix_expression,
            TokenType.SLASH: self.__parse_infix_expression,
            TokenType.ASTERISK: self.__parse_infix_expression,
            TokenType.MOD: self.__parse_infix_expression,
            TokenType.EQ_EQ: self.__parse_infix_expression,
            TokenType.NOT_EQ: self.__parse_infix_expression,
            TokenType.GT: self.__parse_infix_expression,
            TokenType.LT: self.__parse_infix_expression,
            TokenType.GT_EQ: self.__parse_infix_expression,
            TokenType.LT_EQ: self.__parse_infix_expression,
            TokenType.BW_XOR: self.__parse_infix_expression,
            TokenType.BW_OR: self.__parse_infix_expression,
            TokenType.BW_AND: self.__parse_infix_expression,
        }

        self.__next_token()
        self.__next_token()

    def __next_token(self) -> None:
        self.__current_token = self.__peek_token
        self.__peek_token = self.lexer.next_token()

    def __peak_token_is(self, token_type: TokenType) -> bool:
        return cast(Token, self.__peek_token).token_type is token_type

    def __current_token_is(self, token_type: TokenType) -> bool:
        return cast(Token, self.__current_token).token_type is token_type

    def __expect_token(self, token_type: TokenType) -> bool:
        if self.__peak_token_is(token_type):
            self.__next_token()
            return True
        else:
            self.__peek_error(token_type)
            return False

    def __peek_error(self, token_type: TokenType) -> None:
        self.errors.append(
            f"Expected next token to be: {token_type}, got {cast(Token, self.__peek_token).token_type} instead."
        )

    def __no_prefix_parse_fn_error(self, token_type: TokenType) -> None:
        self.errors.append(f"No prefix parse function found for {token_type}")

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
        match self.__current_token.token_type:
            case TokenType.FUNCTION:
                return self.__parse_function_declaration()
            case TokenType.RETURN:
                return self.__parse_return_statement()
            case TokenType.IF:
                return self.__parse_if_statement()
            case TokenType.LET:
                return self.__parse_assignment_statement()
            case TokenType.IDENTIFIER:
                return self.__parse_reassignment_statement()
            case TokenType.WHILE:
                return self.__parse_while_loop()
            case _:
                return self.__parse_expression_statement()

    def __parse_function_declaration(self):
        function_statement: FunctionStatement = FunctionStatement()

        if not self.__expect_token(TokenType.IDENTIFIER):
            return None

        function_statement.function_name = IdentifierLiteral(
            self.__current_token.token_literal
        )

        if not self.__expect_token(TokenType.LPAREN):
            return None

        function_statement.parameters = []

        if not self.__expect_token(TokenType.RPAREN):
            return None

        if not self.__expect_token(TokenType.ARROW):
            return None

        if not self.__expect_token(TokenType.TYPE):
            return None

        function_statement.return_type = self.__current_token.token_literal

        if not self.__expect_token(TokenType.LCURLY):
            return None

        block_statement = self.__parse_block_statement()

        function_statement.body = block_statement

        return function_statement

    def __parse_return_statement(self) -> ReturnStatement:
        return_statement: ReturnStatement = ReturnStatement()
        self.__next_token()

        return_statement.return_value = self.__parse_expression(PrecedenceType.P_LOWEST)

        if not self.__expect_token(TokenType.SEMICOLON):
            return None

        return return_statement

    def __parse_block_statement(self) -> BlockStatement:
        block_statement: BlockStatement = BlockStatement()

        self.__next_token()

        while not self.__current_token_is(
            TokenType.RCURLY
        ) and not self.__current_token_is(TokenType.EOF):
            statement: Statement = self.__parse_statement()
            if statement is not None:
                block_statement.statements.append(statement)

            self.__next_token()

        return block_statement

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

    def __parse_assignment_statement(self) -> Optional[AssignmentStatement]:
        statement: AssignmentStatement = AssignmentStatement()

        if not self.__expect_token(TokenType.IDENTIFIER):
            return None

        statement.identifier = IdentifierLiteral(self.__current_token.token_literal)

        if not self.__expect_token(TokenType.COLON):
            return None

        if not self.__expect_token(TokenType.TYPE):
            return None

        statement.value_type = self.__current_token.token_literal

        if not self.__expect_token(TokenType.EQUALS):
            return None

        self.__next_token()

        statement.value = self.__parse_expression(PrecedenceType.P_LOWEST)

        while not self.__current_token_is(
            TokenType.SEMICOLON
        ) and not self.__current_token_is(TokenType.EOF):
            self.__next_token()

        return statement

    def __parse_reassignment_statement(self):
        reassignment_statement: ReassignmentStatement = ReassignmentStatement()
        reassignment_statement.identifier = IdentifierLiteral(
            self.__current_token.token_literal
        )

        if not self.__expect_token(TokenType.EQUALS):
            return None

        self.__next_token()

        reassignment_statement.value = self.__parse_expression(PrecedenceType.P_LOWEST)

        if not self.__expect_token(TokenType.SEMICOLON):
            return None

        return reassignment_statement

    def __parse_infix_expression(self, left_node: Expression) -> InfixExpression | None:
        infix_expression: InfixExpression = InfixExpression(
            left_node=left_node,
            operator=cast(Token, self.__current_token).token_literal,
            right_node=None,
        )
        precedence = self.__current_precedence()
        self.__next_token()

        if not (right_node := self.__parse_expression(precedence)):
            self.errors.append(
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
            self.errors.append(
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
            self.errors.append(
                f"Could not parse {cast(Token, self.__current_token).token_literal} as a float"
            )
            return None

    def __parse_identifier_literal(self):
        return IdentifierLiteral(self.__current_token.token_literal)

    def __parse_boolean_literal(self):
        return BooleanLiteral(self.__current_token_is(TokenType.TRUE))

    def __parse_bitwise_not_expression(self):
        prefix_expression = PrefixExpression()
        prefix_expression.operator = self.__current_token.token_literal

        self.__next_token()

        prefix_expression.operand = self.__parse_expression(PrecedenceType.P_LOWEST)
        return prefix_expression

    def __parse_if_statement(self):
        if_statement: IfStatement = IfStatement()

        self.__next_token()

        if_statement.condition = self.__parse_expression(PrecedenceType.P_LOWEST)

        if not self.__expect_token(TokenType.LCURLY):
            return None

        if_statement.consequence = self.__parse_block_statement()
        if self.__peak_token_is(TokenType.ELSE):
            self.__next_token()
            if not self.__expect_token(TokenType.LCURLY):
                return None

            if_statement.alternative = self.__parse_block_statement()

        return if_statement

    def __parse_while_loop(self):
        while_loop: WhileLoop = WhileLoop()

        self.__next_token()

        while_loop.condition = self.__parse_expression(PrecedenceType.P_LOWEST)

        if not self.__expect_token(TokenType.LCURLY):
            return None

        while_loop.consequence = self.__parse_block_statement()

        return while_loop
