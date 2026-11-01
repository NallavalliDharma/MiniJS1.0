from tokens import TokenType
from ast_nodes import (
Literal,
Variable,
Unary,
Binary,
Logical,
LetStatement,
Assignment,
PrintStatement,
Block,
IfStatement,
WhileStatement,
)

class ParseError(Exception):
  """Raised when the source code contains a syntax error."""
  pass

class Parser:
  def __init__(self, tokens):
    self.tokens = tokens
    self.current = 0


# ==========================================
# Token navigation helpers
# ==========================================

  def is_at_end(self):
      return self.peek().type == TokenType.EOF

  def peek(self):
      return self.tokens[self.current]

  def previous(self):
      return self.tokens[self.current - 1]

  def advance(self):
      if not self.is_at_end():
          self.current += 1

      return self.previous()

  def check(self, token_type):
      if self.is_at_end():
          return token_type == TokenType.EOF
      return self.peek().type == token_type

  def match(self, *token_types):
      for token_type in token_types:
          if self.check(token_type):
              self.advance()
              return True

      return False

  def consume(self, token_type, message):
      if self.check(token_type):
          return self.advance()

      raise ParseError(
          f"Line {self.peek().line}: {message}"
      )

  # ==========================================
  # Parse the entire program
  # ==========================================

  def parse(self):
      statements = []

      while not self.is_at_end():
          statements.append(self.declaration())

      return statements

  # ==========================================
  # Declarations and statements
  # ==========================================

  def declaration(self):
      if self.match(TokenType.LET):
          return self.let_declaration()

      return self.statement()

  def let_declaration(self):
      name = self.consume(
          TokenType.IDENTIFIER,
          "Expected a variable name after 'let'."
      )

      self.consume(
          TokenType.EQUAL,
          "Expected '=' after the variable name."
      )

      initializer = self.expression()

      self.consume(
          TokenType.SEMICOLON,
          "Expected ';' after variable declaration."
      )

      return LetStatement(name.lexeme, initializer)

  def statement(self):
      if self.match(TokenType.PRINT):
          return self.print_statement()

      if self.match(TokenType.IF):
          return self.if_statement()

      if self.match(TokenType.WHILE):
          return self.while_statement()

      if self.match(TokenType.LEFT_BRACE):
          return self.block_statement()

      if self.check(TokenType.IDENTIFIER):
          return self.assignment_statement()

      raise ParseError(
          f"Line {self.peek().line}: Expected a statement."
      )

  def print_statement(self):
      self.consume(
          TokenType.LEFT_PAREN,
          "Expected '(' after 'print'."
      )

      expression = self.expression()

      self.consume(
          TokenType.RIGHT_PAREN,
          "Expected ')' after the print expression."
      )

      self.consume(
          TokenType.SEMICOLON,
          "Expected ';' after print statement."
      )

      return PrintStatement(expression)

  def assignment_statement(self):
      name = self.advance()

      self.consume(
          TokenType.EQUAL,
          "Expected '=' after the variable name."
      )

      value = self.expression()

      self.consume(
          TokenType.SEMICOLON,
          "Expected ';' after assignment."
      )

      return Assignment(name.lexeme, value)

  def block_statement(self):
      statements = []

      while (
          not self.check(TokenType.RIGHT_BRACE)
          and not self.is_at_end()
      ):
          statements.append(self.declaration())

      self.consume(
          TokenType.RIGHT_BRACE,
          "Expected '}' after block."
      )

      return Block(statements)

  def if_statement(self):
      self.consume(
          TokenType.LEFT_PAREN,
          "Expected '(' after 'if'."
      )

      condition = self.expression()

      self.consume(
          TokenType.RIGHT_PAREN,
          "Expected ')' after if condition."
      )

      self.consume(
          TokenType.LEFT_BRACE,
          "Expected '{' before if body."
      )

      then_branch = self.block_statement()

      else_branch = None

      if self.match(TokenType.ELSE):
          self.consume(
              TokenType.LEFT_BRACE,
              "Expected '{' before else body."
          )

          else_branch = self.block_statement()

      return IfStatement(
          condition,
          then_branch,
          else_branch
      )

  def while_statement(self):
      self.consume(
          TokenType.LEFT_PAREN,
          "Expected '(' after 'while'."
      )

      condition = self.expression()

      self.consume(
          TokenType.RIGHT_PAREN,
          "Expected ')' after while condition."
      )

      self.consume(
          TokenType.LEFT_BRACE,
          "Expected '{' before while body."
      )

      body = self.block_statement()

      return WhileStatement(condition, body)

  # ==========================================
  # Expressions and operator precedence
  # ==========================================

  def expression(self):
      return self.logical_or()

  def logical_or(self):
      expression = self.logical_and()

      while self.match(TokenType.OR):
          operator = self.previous()
          right = self.logical_and()

          expression = Logical(
              expression,
              operator,
              right
          )

      return expression

  def logical_and(self):
      expression = self.equality()

      while self.match(TokenType.AND):
          operator = self.previous()
          right = self.equality()

          expression = Logical(
              expression,
              operator,
              right
          )

      return expression

  def equality(self):
      expression = self.comparison()

      while self.match(
          TokenType.STRICT_EQUAL,
          TokenType.STRICT_NOT_EQUAL
      ):
          operator = self.previous()
          right = self.comparison()

          expression = Binary(
              expression,
              operator,
              right
          )

      return expression

  def comparison(self):
      expression = self.term()

      while self.match(
          TokenType.LESS,
          TokenType.LESS_EQUAL,
          TokenType.GREATER,
          TokenType.GREATER_EQUAL
      ):
          operator = self.previous()
          right = self.term()

          expression = Binary(
              expression,
              operator,
              right
          )

      return expression

  def term(self):
      expression = self.factor()

      while self.match(
          TokenType.PLUS,
          TokenType.MINUS
      ):
          operator = self.previous()
          right = self.factor()

          expression = Binary(
              expression,
              operator,
              right
          )

      return expression

  def factor(self):
      expression = self.unary()

      while self.match(
          TokenType.STAR,
          TokenType.SLASH,
          TokenType.PERCENT
      ):
          operator = self.previous()
          right = self.unary()

          expression = Binary(
              expression,
              operator,
              right
          )

      return expression

  def unary(self):
      if self.match(
          TokenType.NOT,
          TokenType.MINUS,
          TokenType.PLUS
      ):
          operator = self.previous()
          right = self.unary()

          return Unary(operator, right)

      return self.primary()

  def primary(self):
      if self.match(TokenType.FALSE):
          return Literal(False)

      if self.match(TokenType.TRUE):
          return Literal(True)

      if self.match(TokenType.NUMBER):
          return Literal(self.previous().literal)

      if self.match(TokenType.IDENTIFIER):
          return Variable(self.previous().lexeme)

      if self.match(TokenType.LEFT_PAREN):
          expression = self.expression()

          self.consume(
              TokenType.RIGHT_PAREN,
              "Expected ')' after expression."
          )

          return expression

      raise ParseError(
          f"Line {self.peek().line}: Expected an expression."
      )

