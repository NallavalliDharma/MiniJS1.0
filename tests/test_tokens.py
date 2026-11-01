from tokens import Token, TokenType


token = Token(
    type=TokenType.NUMBER,
    lexeme="22",
    literal=22.0,
    line=1
)

print(token)