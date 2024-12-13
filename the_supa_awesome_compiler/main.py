from _lexer import Lexer


if __name__ == "__main__":
    with open("../tests/func.marsh", "r") as f:
        source_code = [line.rstrip() for line in f.readlines()]

print(source_code)
lexer = Lexer(source_code)
print(lexer.next_token())
print(lexer.next_token())
print(lexer.next_token())
print(lexer.next_token())
print(lexer.next_token())
