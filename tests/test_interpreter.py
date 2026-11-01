from lexer import Lexer
from parser import Parser
from interpreter import Interpreter

source = """
let x = 10 + 20 * 3;
print(x);

let y = 100;
y = y + 50;
print(y);

if (x > 50) {
print(true);
} else {
print(false);
}

let i = 0;

while (i < 3) {
print(i);
i = i + 1;
}
"""

tokens = Lexer(source).scan_tokens()
statements = Parser(tokens).parse()

interpreter = Interpreter()
interpreter.interpret(statements)
