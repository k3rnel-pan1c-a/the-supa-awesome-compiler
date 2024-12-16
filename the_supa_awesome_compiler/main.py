import json

from _lexer import Lexer
from _parser import Parser


if __name__ == "__main__":
    with open("../tests/func.marsh", "r") as f:
        source_code = [line.rstrip() for line in f.readlines()]


parser = Parser(Lexer(source_code))
program = parser.parse_program()
with open("../debug/ast.json", "w") as f:
    json.dump(program.json_repr(), f, indent=4)
