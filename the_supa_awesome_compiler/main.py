import json

from the_supa_awesome_compiler._lexer import Lexer
from the_supa_awesome_compiler._parser import Parser
from the_supa_awesome_compiler.compiler import Compiler

if __name__ == "__main__":

    with open("../tests/func.marsh", "r") as f:
        source_code = [line.rstrip() for line in f.readlines()]

    
    parser = Parser(Lexer(source_code))
    program = parser.parse_program()

    
    with open("../debug/ast.json", "w") as f:
        json.dump(program.json_repr(), f, indent=4)

    
    compiler = Compiler()
    compiler.compile(program)

   
    ir_text = str(compiler.module)
    with open("ir.ll", "w") as f:
        f.write(ir_text)

    print("Compilation complete! IR written to ir.ll")
