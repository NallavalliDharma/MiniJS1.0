from tokens import Token, TokenType


KEYWORDS = {
    "let": TokenType.LET,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "print": TokenType.PRINT,
}


class Lexer:
    def __init__(self, source):
        self.source = source
        self.tokens = []

        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(
            Token(TokenType.EOF, "", None, self.line)
        )

        return self.tokens

    def is_at_end(self):
        return self.current >= len(self.source)

    def advance(self):
        char = self.source[self.current]
        self.current += 1
        return char

    def peek(self):
        if self.is_at_end():
            return "\0"

        return self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return "\0"

        return self.source[self.current + 1]

    def match(self, expected):
        if self.is_at_end():
            return False

        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def add_token(self, token_type, literal=None):
        text = self.source[self.start:self.current]

        self.tokens.append(
            Token(
                type=token_type,
                lexeme=text,
                literal=literal,
                line=self.line
            )
        )

    def scan_token(self):
        char = self.advance()

        if char in " \r\t":
            return

        if char == "\n":
            self.line += 1
            return

        if char == "(":
            self.add_token(TokenType.LEFT_PAREN)
        elif char == ")":
            self.add_token(TokenType.RIGHT_PAREN)
        elif char == "{":
            self.add_token(TokenType.LEFT_BRACE)
        elif char == "}":
            self.add_token(TokenType.RIGHT_BRACE)
        elif char == ";":
            self.add_token(TokenType.SEMICOLON)

        elif char == "+":
            self.add_token(TokenType.PLUS)
        elif char == "-":
            self.add_token(TokenType.MINUS)
        elif char == "*":
            self.add_token(TokenType.STAR)
        elif char == "%":
            self.add_token(TokenType.PERCENT)

        elif char == "!":
            if self.match("="):
                if self.match("="):
                    self.add_token(TokenType.STRICT_NOT_EQUAL)
                else:
                    self.error("Unsupported operator '!='" )
            else:
                self.add_token(TokenType.NOT)

        elif char == "=":
            if self.match("="):
                if self.match("="):
                    self.add_token(TokenType.STRICT_EQUAL)
                else:
                    self.error("Unsupported operator '=='")
            else:
                self.add_token(TokenType.EQUAL)

        elif char == "<":
            if self.match("="):
                self.add_token(TokenType.LESS_EQUAL)
            else:
                self.add_token(TokenType.LESS)

        elif char == ">":
            if self.match("="):
                self.add_token(TokenType.GREATER_EQUAL)
            else:
                self.add_token(TokenType.GREATER)

        elif char == "&":
            if self.match("&"):
                self.add_token(TokenType.AND)
            else:
                self.error("Unexpected character '&'")

        elif char == "|":
            if self.match("|"):
                self.add_token(TokenType.OR)
            else:
                self.error("Unexpected character '|'")

        elif char == "/":
            if self.match("/"):
                while self.peek() not in ("\n", "\0"):
                    self.advance()
            elif self.match("*"):
                self.block_comment()
            else:
                self.add_token(TokenType.SLASH)

        elif char.isascii() and char.isdigit():
            self.number()

        elif self.is_identifier_start(char):
            self.identifier()

        else:
            self.error(f"Unexpected character {char!r}")

    def number(self):
        while self.peek().isascii() and self.peek().isdigit():
            self.advance()

        if self.peek() == "." and self.peek_next().isascii() and self.peek_next().isdigit():
            self.advance()

            while self.peek().isascii() and self.peek().isdigit():
                self.advance()

        text = self.source[self.start:self.current]
        value = float(text)

        self.add_token(TokenType.NUMBER, value)

    def identifier(self):
        while self.is_identifier_part(self.peek()):
            self.advance()

        text = self.source[self.start:self.current]

        token_type = KEYWORDS.get(text, TokenType.IDENTIFIER)

        literal = None

        if token_type == TokenType.TRUE:
            literal = True
        elif token_type == TokenType.FALSE:
            literal = False

        self.add_token(token_type, literal)

    @staticmethod
    def is_identifier_start(char):
        return (
            char == "_"
            or char == "$"
            or ("a" <= char <= "z")
            or ("A" <= char <= "Z")
        )

    @staticmethod
    def is_identifier_part(char):
        return (
            Lexer.is_identifier_start(char)
            or ("0" <= char <= "9")
        )

    def block_comment(self):
        while not self.is_at_end():
            if self.peek() == "*" and self.peek_next() == "/":
                self.advance()
                self.advance()
                return

            if self.peek() == "\n":
                self.line += 1

            self.advance()

        self.error("Unterminated block comment")

    def error(self, message):
        raise SyntaxError(f"Line {self.line}: {message}")

