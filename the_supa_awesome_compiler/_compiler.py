from llvmlite import ir

from _AST import (
    Node,
    NodeType,
    Program,
    Expression,
    Statement,
    ExpressionStatement,
    AssignmentStatement,
    FunctionStatement,
    BlockStatement,
    ReturnStatement,
    ReassignmentStatement,
    InfixExpression,
    IntegerLiteral,
    FloatLiteral,
    IdentifierLiteral,
)
from _environment import Environment

from typing import cast, Optional


class Compiler:
    def __init__(self):
        self.__type_map = {"int": ir.IntType(32), "float": ir.FloatType()}
        self.module = ir.Module("main_module")
        self.__builder: Optional[ir.IRBuilder] = None
        self.__environment = Environment()

    def compile(self, node: Node):
        match node.type():
            case NodeType.PROGRAM:
                self.__visit_program(cast(Program, node))

            case NodeType.FUNCTION_STATEMENT:
                self.__visit_function_statement(cast(FunctionStatement, node))

            case NodeType.BLOCK_STATEMENT:
                self.__visit_block_statement(cast(BlockStatement, node))

            case NodeType.RETURN_STATEMENT:
                self.__visit_return_statement(cast(ReturnStatement, node))

            case NodeType.EXPRESSION_STATEMENT:
                self.__visit_expression_statement(cast(ExpressionStatement, node))

            case NodeType.ASSIGNMENT_STATEMENT:
                self.__visit_assignment_statement(cast(AssignmentStatement, node))

            case NodeType.REASSIGNMENT_STATEMENT:
                self.__visit_reassignment_statement(cast(ReassignmentStatement, node))
            case NodeType.INFIX_EXPRESSION:
                self.__visit_infix_expression(cast(InfixExpression, node))

    def __visit_program(self, node: Program):
        for stmt in node.statements:
            self.compile(stmt)

    def __visit_function_statement(self, node: FunctionStatement):
        name: str = node.function_name.identifier_literal
        body: BlockStatement = node.body

        parameter_types: list[ir.Type] = []

        return_type: ir.Type = self.__type_map[node.return_type]

        function_type: ir.FunctionType = ir.FunctionType(return_type, parameter_types)
        function: ir.Function = ir.Function(self.module, function_type, name=name)

        block: ir.Block = function.append_basic_block(f"{name}_entry")

        self.builder: ir.IRBuilder = ir.IRBuilder(block)

        prev_builder = self.__builder

        self.__builder = ir.IRBuilder(block)

        prev_environment = self.__environment

        self.__environment = Environment(parent=self.__environment)
        self.__environment.define(name, function, return_type)

        self.compile(
            body
        )  # Need to change the environment to prev and current to allow for recursive calls

        self.__environment = prev_environment
        self.__environment.define(name, function, return_type)

        self.__builder = prev_builder

    def __visit_block_statement(self, node: BlockStatement):
        for statement in node.statements:
            self.compile(statement)

    def __visit_return_statement(self, node: ReturnStatement):
        value: Expression = node.return_value
        value, type = self.__resolve_value(value)

        self.__builder.ret(value)

    def __visit_assignment_statement(self, node: AssignmentStatement):
        identifier: IdentifierLiteral = node.identifier

        value, type = self.__resolve_value(node.value)

        if self.__environment.lookup(identifier.identifier_literal) is None:
            ptr = self.__builder.alloca(type)
            self.__builder.store(value, ptr)

            self.__environment.define(identifier.identifier_literal, ptr, type)
        else:
            ptr, _ = self.__environment.lookup(
                identifier.identifier_literal
            )  # Need to restrict this to only the
            # current scope
            self.__builder.store(value, ptr)

    def __visit_reassignment_statement(self, node: ReassignmentStatement):
        identifier: IdentifierLiteral = node.identifier
        value: Expression = node.value

        ptr, _ = self.__environment.lookup(identifier.identifier_literal)
        value, _ = self.__resolve_value(value)

        self.__builder.store(value, ptr)

    def __visit_expression_statement(self, node: ExpressionStatement):
        self.compile(node.expression)

    def __visit_infix_expression(self, node: InfixExpression):
        left_val, left_type = self.__resolve_value(node.left_node)
        right_val, right_type = self.__resolve_value(node.right_node)

        operator = node.operator

        if isinstance(left_type, ir.IntType) and isinstance(right_type, ir.IntType):
            match operator:
                case "+":
                    result = self.__builder.add(left_val, right_val)
                case "-":
                    result = self.__builder.sub(left_val, right_val)
                case "*":
                    result = self.__builder.mul(left_val, right_val)
                case "/":
                    result = self.__builder.sdiv(left_val, right_val)
                case "%":
                    result = self.__builder.srem(left_val, right_val)
                case _:
                    print(f"Unsupported operator {operator}")
                    return None, None
            return result, self.__type_map["int"]

        return None, None

    def __resolve_value(self, node: Expression | Statement, value_type: str = None):
        match node.type():
            case NodeType.INTEGER_LITERAL:
                node: IntegerLiteral = cast(IntegerLiteral, node)
                value, node_type = node.int_literal, self.__type_map["int"]
                return ir.Constant(node_type, value), node_type

            case NodeType.FLOAT_LITERAL:
                node: FloatLiteral = cast(FloatLiteral, node)
                value, node_type = node.float_literal, self.__type_map["float"]
                return ir.Constant(node_type, value), node_type

            case NodeType.IDENTIFIER_LITERAL:
                node: IdentifierLiteral = cast(IdentifierLiteral, node)
                ptr, type = self.__environment.lookup(node.identifier_literal)
                return self.__builder.load(ptr), type

            case NodeType.INFIX_EXPRESSION:
                node: InfixExpression = cast(InfixExpression, node)
                return self.__visit_infix_expression(node)
