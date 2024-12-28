from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, cast


class NodeType(Enum):
    PROGRAM = "PROGRAM"
    STATEMENT = "STATEMENT"

    # STATEMENTS
    EXPRESSION_STATEMENT = "EXPRESSION_STATEMENT"
    ASSIGNMENT_STATEMENT = "ASSIGNMENT_STATEMENT"
    FUNCTION_STATEMENT = "FUNCTION_STATEMENT"
    BLOCK_STATEMENT = "BLOCK_STATEMENT"
    RETURN_STATEMENT = "RETURN_STATEMENT"
    REASSIGNMENT_STATEMENT = "REASSIGNMENT_STATEMENT"
    IF_STATEMENT = "IF_STATEMENT"

    # EXPRESSIONS
    INFIX_EXPRESSION = "INFIX_EXPRESSION"
    PREFIX_EXPRESSION = "PREFIX_EXPRESSION"
    BOOLEAN_EXPRESSION = "BOOLEAN_EXPRESSION"

    # LITERALS
    INTEGER_LITERAL = "INTEGER_LITERAL"
    FLOAT_LITERAL = "FLOAT_LITERAL"
    IDENTIFIER_LITERAL = "IDENTIFIER_LITERAL"

    # LOOPS
    WHILE_LOOP = "WHILE_LOOP"
    FOR_LOOP = "FOR_LOOP"


class Node(ABC):
    @abstractmethod
    def type(self) -> NodeType:
        pass

    @abstractmethod
    def json_repr(self) -> dict:
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


class IdentifierLiteral(Expression):
    def __init__(self, identifier: str):
        self.identifier_literal = identifier

    def type(self) -> NodeType:
        return NodeType.IDENTIFIER_LITERAL

    def json_repr(self) -> dict:
        return {"type": self.type().value, "identifier": self.identifier_literal}


class BlockStatement(Statement):
    def __init__(self, statements: list[Statement] = None):
        self.statements = statements if statements else []

    def type(self) -> NodeType:
        return NodeType.BLOCK_STATEMENT

    def json_repr(self) -> dict:
        return {
            "type": self.type().value,
            "statements": [statement.json_repr() for statement in self.statements],
        }


class ReturnStatement(Statement):
    def __init__(self, return_value: Expression = None):
        self.return_value = return_value

    def type(self) -> NodeType:
        return NodeType.RETURN_STATEMENT

    def json_repr(self) -> dict:
        return {"type": self.type().value, "expression": self.return_value.json_repr()}


class FunctionStatement(Statement):
    def __init__(
        self,
        parameters: list[IdentifierLiteral] = None,
        body: BlockStatement = None,
        function_name: IdentifierLiteral = None,
        return_type: str = None,
    ):
        self.function_name = function_name
        self.parameters = parameters if parameters else []
        self.body = body
        self.return_type = return_type

    def type(self) -> NodeType:
        return NodeType.FUNCTION_STATEMENT

    def json_repr(self) -> dict:
        return {
            "type": self.type().value,
            "name": self.function_name.identifier_literal,
            "parameters": [parameter.json_repr() for parameter in self.parameters],
            "body": self.body.json_repr(),
            "return_type": self.return_type,
        }


class IfStatement(Statement):
    def __init__(
        self,
        condition: Expression = None,
        consequence: BlockStatement = None,
        alternative: BlockStatement = None,
    ):
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative if alternative is not None else BlockStatement()

    def type(self) -> NodeType:
        return NodeType.IF_STATEMENT

    def json_repr(self) -> dict:
        return {
            "type": self.type().value,
            "condition": self.condition.json_repr(),
            "consequence": self.consequence.json_repr(),
            "alternative": self.alternative.json_repr(),
        }


class AssignmentStatement(Statement):
    def __init__(
        self,
        identifier: IdentifierLiteral = None,
        value: Expression = None,
        value_type: str = None,
    ):
        self.identifier = identifier
        self.value = value
        self.value_type = value_type

    def type(self):
        return NodeType.ASSIGNMENT_STATEMENT

    def json_repr(self) -> dict:
        return {
            "type": self.type().value,
            "identifier": self.identifier.identifier_literal,
            "value": self.value.json_repr(),
            "value_type": self.value_type,
        }


class ReassignmentStatement(Statement):
    def __init__(self, identifier: IdentifierLiteral = None, value: Expression = None):
        self.identifier = identifier
        self.value = value

    def type(self) -> NodeType:
        return NodeType.REASSIGNMENT_STATEMENT

    def json_repr(self) -> dict:
        return {
            "type": self.type().value,
            "identifier": self.identifier.json_repr(),
            "value": self.value.json_repr(),
        }


class InfixExpression(Expression):
    def __init__(self, left_node: Expression, operator: str, right_node: Expression):
        self.left_node = left_node
        self.operator = operator
        self.right_node = right_node

    def type(self) -> NodeType:
        return NodeType.INFIX_EXPRESSION

    def json_repr(self) -> dict:
        return {
            "type": self.type().value,
            "left_node": self.left_node.json_repr(),
            "operator": self.operator,
            "right_node": self.right_node.json_repr(),
        }


class PrefixExpression(Expression):
    def __init__(self, operator: str = None, operand: Expression = None):
        self.operator = operator
        self.operand = operand

    def type(self) -> NodeType:
        return NodeType.PREFIX_EXPRESSION

    def json_repr(self) -> dict:
        return {
            "type": self.type().value,
            "operator": self.operator,
            "operand": self.operand.json_repr(),
        }


class IntegerLiteral(Expression):
    def __init__(self, int_literal: Optional[int] = None):
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


class BooleanLiteral(Expression):
    def __init__(self, boolean_value: bool = None):
        self.boolean_value = boolean_value

    def type(self) -> NodeType:
        return NodeType.BOOLEAN_EXPRESSION

    def json_repr(self) -> dict:
        return {"type": self.type().value, "boolean_value": self.boolean_value}


class WhileLoop(Statement):
    def __init__(
        self,
        condition: Expression = None,
        consequence: BlockStatement = None,
        alternative: BlockStatement = None,
    ):
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative if alternative is not None else BlockStatement()

    def type(self) -> NodeType:
        return NodeType.WHILE_LOOP

    def json_repr(self) -> dict:
        return {
            "type": self.type().value,
            "condition": self.condition.json_repr(),
            "consequence": self.consequence.json_repr(),
            "alternative": self.alternative.json_repr(),
        }


class ForLoop(Statement):
    def __init__(
        self,
        identifier: IdentifierLiteral = None,
        range_start: IntegerLiteral = None,
        block_statement: BlockStatement = None,
        condition: InfixExpression = None,
        range_end: IntegerLiteral = None,
    ):
        self.identifier = identifier
        self.range_start = range_start
        self.block_statement = block_statement
        self.condition = condition
        self.range_end = range_end

    def type(self):
        return NodeType.FOR_LOOP

    def json_repr(self) -> dict:
        return {
            "type": self.type().value,
            "identifier": self.identifier.json_repr(),
            "range_start": self.range_start.json_repr(),
            "block_statement": self.block_statement.json_repr(),
            "range_end": self.range_end.json_repr(),
        }
