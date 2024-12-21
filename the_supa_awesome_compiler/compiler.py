from llvmlite import ir

from the_supa_awesome_compiler._AST import (
    Node,
    NodeType,
    Program,
    ExpressionStatement,
    InfixExpression,
    IntegerLiteral,
    FloatLiteral,
)

class Compiler:
    def __init__(self):
        self.type_map = {
            'int': ir.IntType(32),
            'float': ir.FloatType()
        }
        self.module = ir.Module('my_module')
        self.builder = None

    def compile(self, node: Node):
        """
        Main entry point for compiling a node. We'll match on the node type
        and dispatch to helper methods.
        """
        ntype = node.type()

        if ntype == NodeType.PROGRAM:
            return self._visit_program(node)
        elif ntype == NodeType.EXPRESSION_STATEMENT:
            return self._visit_expression_statement(node)
        elif ntype == NodeType.INFIX_EXPRESSIONS:
            return self._visit_infix_expression(node)
        elif ntype == NodeType.INTEGER_LITERAL:
            return self._visit_integer_literal(node)
        elif ntype == NodeType.FLOAT_LITERAL:
            return self._visit_float_literal(node)
        else:
            print(f"Unrecognized node type: {ntype}")
            return None

    def _visit_program(self, node: Program):
        """
        Create a main function that returns int and build its body.
        """
        func_type = ir.FunctionType(self.type_map['int'], [])
        main_func = ir.Function(self.module, func_type, name="main")

        block = main_func.append_basic_block('entry')
        self.builder = ir.IRBuilder(block)


        for stmt in node.statements:
            self.compile(stmt)

        ret_val = ir.Constant(self.type_map['int'], 0)
        self.builder.ret(ret_val)

    def _visit_expression_statement(self, node: ExpressionStatement):
        """
        ExpressionStatements in this example just compile the inner expression
        and discard its result (not stored anywhere).
        """
        return self.compile(node.expression)

    def _visit_infix_expression(self, node: InfixExpression):
        """
        e.g. left_node operator right_node
        """
        left_val, left_type = self._resolve_value(node.left_node)
        right_val, right_type = self._resolve_value(node.right_node)
        
        operator = node.operator
        result = None


        if isinstance(left_type, ir.IntType) and isinstance(right_type, ir.IntType):
            if operator == '+':
                result = self.builder.add(left_val, right_val, name="addtmp")
            elif operator == '-':
                result = self.builder.sub(left_val, right_val, name="subtmp")
            elif operator == '*':
                result = self.builder.mul(left_val, right_val, name="multmp")
            elif operator == '/':

                result = self.builder.sdiv(left_val, right_val, name="divtmp")
            else:
                print(f"Unsupported operator {operator}")
                return None, None
            return result, self.type_map['int']
        

        return None, None

    def _resolve_value(self, node):
        """
        Returns (llvm_value, llvm_type) for the given AST node.
        """
        result = self.compile(node)
        if isinstance(result, tuple):
            return result

        return result, self.type_map['int']

    def _visit_integer_literal(self, node: IntegerLiteral):
        """
        Create a constant i32 in LLVM
        """
        val = node.int_literal  # e.g. 5
        llvm_val = ir.Constant(self.type_map['int'], val)
        return llvm_val, self.type_map['int']

    def _visit_float_literal(self, node: FloatLiteral):
        """
        Create a constant float in LLVM
        """
        val = node.float_literal  # e.g. 3.14
        llvm_val = ir.Constant(self.type_map['float'], val)
        return llvm_val, self.type_map['float']

