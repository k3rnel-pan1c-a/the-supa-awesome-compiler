import json

from _lexer import Lexer
from _parser import Parser
from _compiler import Compiler

from llvmlite import ir
import llvmlite.binding as llvm
from ctypes import CFUNCTYPE, c_int

LEXER_DEBUG: bool = False
COMPILER_DEBUG: bool = False
RUN_PARSER: bool = True
RUN_COMPILER: bool = True
RUN_CODE: bool = True

if __name__ == "__main__":
    with open("../tests/func.marsh", "r") as f:
        source_code = [line for line in f.readlines()]

    if LEXER_DEBUG:
        print("======DEBUG LEXER======")
        debug_lexer = Lexer(source_code)
        while debug_lexer.current_char is not None:
            print(debug_lexer.next_token())
    if RUN_PARSER:
        parser = Parser(Lexer(source_code))
        program = parser.parse_program()
        print(program.json_repr())
        with open("../debug/ast.json", "w") as f:
            json.dump(program.json_repr(), f, indent=4)

    if COMPILER_DEBUG:
        if len(parser.errors):
            for err in parser.errors:
                print(err)

            exit(1)

    if RUN_COMPILER:
        compiler = Compiler()

        # try:
        compiler.compile(program)
        #
        # except Exception as e:
        #     print(e)
        #     exit(1)

        module: ir.Module = compiler.module
        module.triple = llvm.get_default_triple()

        with open("../debug/ir.ll", "w") as f:
            f.write(str(module))

        print("Compilation complete! IR written to ir.ll")

    if RUN_CODE:
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_all_asmprinters()
        try:
            llvm_ir_parsed = llvm.parse_assembly(str(module))
            llvm_ir_parsed.verify()
        except Exception as e:
            print(e)

        target_machine = llvm.Target.from_default_triple().create_target_machine()

        engine = llvm.create_mcjit_compiler(llvm_ir_parsed, target_machine)
        engine.finalize_object()

        entry = engine.get_function_address("main")
        cfunction = CFUNCTYPE(c_int)(entry)

        result = cfunction()

        print(result)
