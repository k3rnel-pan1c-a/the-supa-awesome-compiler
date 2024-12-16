from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, cast


class NodeType(Enum):
    PROGRAM = "PROGRAM"
    STATEMENT = "STATEMENT"

    # STATEMENTS
    EXPRESSION_STATEMENT = "EXPRESSION_STATEMENT"

    # EXPRESSIONS
    INFIX_EXPRESSIONS = "INFIX_EXPRESSIONS"

    PREFIX_EXPRESSIONS = "PREFIX_EXPRESSIONS"

    # LITERALS
    INTEGER_LITERAL = "INTEGER_LITERAL"

    FLOAT_LITERAL = "FLOAT_LITERAL"


class Node(ABC):
    @abstractmethod
    def type(self) -> NodeType:
        pass

    @abstractmethod
    def json_repr(self) -> dict[str, dict]:
        pass


class Statement(Node):
    pass


class Expression(Node):
    pass


class Program(Node):
    def __init__(self):
        self.statements: list[
            Statement
        ] = []  # I'm assuming we do this for statements and we eval expressions

    def type(self) -> NodeType:
        return NodeType.PROGRAM

    def json_repr(self) -> dict:
        return {
            "type": self.type().value,
            "statements": [
                {statement.type().value: statement.json_repr()}
                for statement in self.statements
            ],
        }


class ExpressionStatement(Statement):
    def __init__(self, expression: Optional[Expression] = None):
        self.expression = expression

    def type(self) -> NodeType:
        return NodeType.EXPRESSION_STATEMENT

    def json_repr(self) -> dict:
        return {
            "type": self.type().value,
            "expression": cast(Expression, self.expression).json_repr(),
        }


class InfixExpression(Expression):
    def __init__(self, left_node: Expression, operator: str, right_node: Expression):
        self.left_node = left_node
        self.operator = operator
        self.right_node = right_node

    def type(self) -> NodeType:
        return NodeType.INFIX_EXPRESSIONS

    def json_repr(self) -> dict:
        return {
            "type": self.type().value,
            "left_node": self.left_node.json_repr(),
            "operator": self.operator,
            "right_node": self.right_node.json_repr(),
        }


class IntegerLiteral(Expression):
    def __init__(self, int_literal: Optional[None] = None):
        self.int_literal = int_literal

    def type(self) -> NodeType:
        return NodeType.INTEGER_LITERAL

    def json_repr(self) -> dict:
        return {"type": self.type().value, "literal": self.int_literal}


class FloatLiteral(Expression):
    def __init__(self, float_literal: Optional[float] = None):
        self.float_literal = float_literal

    def type(self) -> NodeType:
        return NodeType.FLOAT_LITERAL

    def json_repr(self) -> dict:
        return {"type": self.type().value, "literal": self.float_literal}
