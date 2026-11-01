from lexer import Lexer
from parser import Parser

source = """
let x = 10 + 20 * 3;
print(x);
"""

tokens = Lexer(source).scan_tokens()
statements = Parser(tokens).parse()

for statement in statements:
  print(statement)
