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
    IfStatement,
    WhileLoop,
    ForLoop,
    BooleanLiteral,
    PrefixExpression,
    InfixExpression,
    CallExpression,
    IntegerLiteral,
    FloatLiteral,
    IdentifierLiteral,
)
from _environment import Environment

from typing import cast, Optional


class Compiler:
    def __init__(self):
        self.errors = []

        self.__type_map = {
            "int": ir.IntType(32),
            "float": ir.FloatType(),
            "bool": ir.IntType(1),
        }
        self.module = ir.Module("main_module")
        self.__builder: Optional[ir.IRBuilder] = None
        self.__environment = Environment()

        self.__initialize_builtins()

    def __initialize_builtins(self):
        def __initialize_booleans():
            bool_type: ir.Type = self.__type_map["bool"]

            true_const = ir.GlobalVariable(self.module, bool_type, "true")
            true_const.initializer = ir.Constant(bool_type, 1)
            true_const.global_constant = True

            false_const = ir.GlobalVariable(self.module, bool_type, "false")
            false_const.initializer = ir.Constant(bool_type, 0)
            false_const.global_constant = True

            return true_const, false_const

        true_const, false_const = __initialize_booleans()

        self.__environment.define("true", true_const, true_const.type)
        self.__environment.define("false", false_const, false_const.type)

    def __visit_parent_environment(
        self, environment: Environment, node: IdentifierLiteral
    ):
        if (
            environment.lookup(node.identifier_literal) is None
            and environment.parent is not None
        ):
            return self.__visit_parent_environment(environment.parent, node)

        else:
            if environment.lookup(node.identifier_literal) is None:
                self.errors.append(f"Undefined variable {node.identifier_literal}")
                raise Exception(
                    f"Exception occurred: Undefined variable '{node.identifier_literal}'"
                )

            else:
                return environment.lookup(node.identifier_literal)

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

            case NodeType.IF_STATEMENT:
                self.__visit_if_statement(cast(IfStatement, node))

            case NodeType.INFIX_EXPRESSION:
                self.__visit_infix_expression(cast(InfixExpression, node))

            case NodeType.PREFIX_EXPRESSION:
                self.__visit_prefix_expression(cast(PrefixExpression, node))

            case NodeType.WHILE_LOOP:
                self.__visit_while_loop(cast(WhileLoop, node))

            case NodeType.FOR_LOOP:
                self.__visit_for_loop(cast(ForLoop, node))

            case NodeType.FUNCTION_CALL:
                self.__visit_function_call(cast(CallExpression, node))

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

        self.__builder = self.builder

        prev_environment = self.__environment

        self.__environment = Environment(parent=self.__environment)
        self.__environment.define(name, function, return_type)

        self.compile(body)

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
            ptr, _ = self.__visit_parent_environment(self.__environment, identifier)
            #     ptr, _ = self.__environment.lookup(
            #         identifier.identifier_literal
            #     )  # Need to restrict this to only the
            # # current scope
            self.__builder.store(value, ptr)

    def __visit_reassignment_statement(self, node: ReassignmentStatement):
        identifier: IdentifierLiteral = node.identifier
        value: Expression = node.value

        ptr, _ = self.__visit_parent_environment(self.__environment, identifier)
        # ptr, _ = self.__environment.lookup(identifier.identifier_literal)
        value, _ = self.__resolve_value(value)
        self.__builder.store(value, ptr)

    def __visit_if_statement(self, node: IfStatement):
        condition = node.condition
        consequence = node.consequence
        alternative = node.alternative

        prev_environment = self.__environment
        self.__environment = Environment(parent=self.__environment)

        value, _ = self.__resolve_value(condition)

        if not alternative.statements:
            with self.__builder.if_then(value):
                self.compile(consequence)
        else:
            with self.__builder.if_else(value) as (then, otherwise):
                with then:
                    self.compile(consequence)

                with otherwise:
                    self.compile(alternative)

        self.__environment = prev_environment

    def __visit_while_loop(self, node: WhileLoop):
        condition = node.condition
        consequence = node.consequence

        prev_environment = self.__environment
        self.__environment = Environment(parent=self.__environment)

        value, _ = self.__resolve_value(condition)

        while_loop_entry = self.__builder.append_basic_block("while_loop_entry")
        while_loop_otherwise = self.__builder.append_basic_block("while_loop_otherwise")

        self.__builder.cbranch(value, while_loop_entry, while_loop_otherwise)

        self.__builder.position_at_start(while_loop_entry)
        self.compile(consequence)
        value, _ = self.__resolve_value(condition)
        self.__builder.cbranch(value, while_loop_entry, while_loop_otherwise)
        self.__builder.position_at_start(while_loop_otherwise)

        self.__environment = prev_environment

    def __visit_for_loop(self, node: ForLoop):
        identifier = node.identifier
        range_start = node.range_start
        block_statement = node.block_statement
        condition = node.condition

        prev_environment = self.__environment

        self.__environment = Environment(parent=self.__environment)

        ptr = self.__builder.alloca(self.__type_map["int"])
        self.__builder.store(
            ir.Constant(self.__type_map["int"], range_start.int_literal), ptr
        )

        self.__environment.define(
            identifier.identifier_literal, ptr, self.__type_map["int"]
        )

        for_loop_entry = self.__builder.append_basic_block("for_loop_entry")
        for_loop_otherwise = self.__builder.append_basic_block("for_loop_otherwise")

        value, _ = self.__resolve_value(condition)
        self.__builder.cbranch(value, for_loop_entry, for_loop_otherwise)

        self.__builder.position_at_start(for_loop_entry)
        self.compile(block_statement)
        current_value = self.__builder.load(ptr)
        result = self.__builder.add(current_value, ir.Constant(ir.IntType(32), 1))

        self.__builder.store(result, ptr)

        value, _ = self.__resolve_value(condition)
        self.__builder.cbranch(value, for_loop_entry, for_loop_otherwise)
        self.__builder.position_at_start(for_loop_otherwise)

        self.__environment = prev_environment

    def __visit_function_call(self, node: CallExpression):
        function_name = node.function_name.identifier_literal

        args = []

        match function_name:
            case _:
                func, ret_type = self.__visit_parent_environment(
                    self.__environment, node.function_name
                )
                ret = self.__builder.call(func, args)

        return ret, ret_type

    def __visit_expression_statement(self, node: ExpressionStatement):
        self.compile(node.expression)

    def __visit_prefix_expression(self, node: PrefixExpression):
        operand_value, operand_type = self.__resolve_value(node.operand)
        operator = node.operator

        if isinstance(operand_type, ir.IntType):
            match operator:
                case "~":
                    result = self.__builder.not_(operand_value)
                    return result, self.__type_map["int"]

                case _:
                    return None, None

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
                case "^":
                    result = self.__builder.xor(left_val, right_val)
                case "&":
                    result = self.__builder.and_(left_val, right_val)
                case "|":
                    result = self.__builder.or_(left_val, right_val)
                case "<":
                    result = self.__builder.icmp_signed("<", left_val, right_val)
                case ">":
                    result = self.__builder.icmp_signed(">", left_val, right_val)
                case ">=":
                    result = self.__builder.icmp_signed(">=", left_val, right_val)
                case "<=":
                    result = self.__builder.icmp_signed("<=", left_val, right_val)
                case "==":
                    result = self.__builder.icmp_signed("==", left_val, right_val)

                case _:
                    print(f"Unsupported operator {operator}")
                    return None, None
            return result, self.__type_map["int"]

        return None, None

    def __resolve_value(self, node: Expression | Statement):
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
                ptr, node_type = self.__visit_parent_environment(
                    self.__environment, node
                )
                return self.__builder.load(ptr), node_type

            case NodeType.BOOLEAN_EXPRESSION:  # Load the boolean values from the symbol table
                node: BooleanLiteral = cast(BooleanLiteral, node)
                # value, node_type = self.__environment.lookup(node.boolean_value.)
                value, node_type = node.boolean_value, self.__type_map["bool"]
                return ir.Constant(node_type, 1 if value else 0), node_type

            case NodeType.INFIX_EXPRESSION:
                node: InfixExpression = cast(InfixExpression, node)
                return self.__visit_infix_expression(node)

            case NodeType.PREFIX_EXPRESSION:
                node: PrefixExpression = cast(PrefixExpression, node)
                return self.__visit_prefix_expression(node)

            case NodeType.FUNCTION_CALL:
                node: CallExpression = cast(CallExpression, node)
                return self.__visit_function_call(node)
