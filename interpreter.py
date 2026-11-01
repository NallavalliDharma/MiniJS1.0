import math
from tokens import TokenType
from environment import Environment
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

from compiler import BytecodeCompiler, execute_bytecode


class InterpreterError(Exception):
    pass


class Interpreter:
  def __init__(self):
    self.environment = Environment()

  # ==========================================
  # Execute a complete program
  # ==========================================

  def interpret(self, statements):
    compiler = BytecodeCompiler()
    code, max_regs = compiler.compile(statements)
    execute_bytecode(code, max_regs)

           
  # ==========================================
  # Execute statements
  # ==========================================

  def execute(self, statement):
    if isinstance(statement, LetStatement):
        self.environment.declare(statement.name)
        value = self.evaluate(statement.initializer)
        self.environment.initialize(statement.name, value)

    elif isinstance(statement, Assignment):
        value = self.evaluate(statement.value)
        self.environment.assign(statement.name, value)

    elif isinstance(statement, PrintStatement):
        value = self.evaluate(statement.expression)
        print(self.stringify(value))

    elif isinstance(statement, Block):
        self.execute_block(
            statement.statements,
            Environment(enclosing=self.environment)
        )

    elif isinstance(statement, IfStatement):
        if self.is_truthy(self.evaluate(statement.condition)):
            self.execute(statement.then_branch)
        elif statement.else_branch is not None:
            self.execute(statement.else_branch)

    elif isinstance(statement, WhileStatement):
        while self.is_truthy(self.evaluate(statement.condition)):
            self.execute(statement.body)

    else:
        raise InterpreterError(
            f"Unknown statement type: {type(statement).__name__}"
        )

  def execute_block(self, statements, environment):
    previous_environment = self.environment

    try:
        self.environment = environment

        for statement in statements:
            self.execute(statement)

    finally:
        self.environment = previous_environment

  # ==========================================
  # Evaluate expressions
  # ==========================================

  def evaluate(self, expression):
    if isinstance(expression, Literal):
        return expression.value

    if isinstance(expression, Variable):
        return self.environment.get(expression.name)

    if isinstance(expression, Unary):
        return self.evaluate_unary(expression)

    if isinstance(expression, Logical):
        return self.evaluate_logical(expression)

    if isinstance(expression, Binary):
        return self.evaluate_binary(expression)

    raise InterpreterError(
        f"Unknown expression type: {type(expression).__name__}"
    )

  def evaluate_unary(self, expression):
    operator = expression.operator.type
    right = self.evaluate(expression.right)

    if operator == TokenType.NOT:
        return not self.is_truthy(right)

    if operator == TokenType.MINUS:
        return -self.require_number(right, expression.operator)

    if operator == TokenType.PLUS:
        return self.require_number(right, expression.operator)

    raise InterpreterError("Unsupported unary operator.")

  def evaluate_logical(self, expression):
    left = self.evaluate(expression.left)
    if expression.operator.type == TokenType.OR:
        if self.is_truthy(left):
            return left
        return self.evaluate(expression.right)
    if expression.operator.type == TokenType.AND:
        if not self.is_truthy(left):
            return left
        return self.evaluate(expression.right)
    raise InterpreterError("Unknown logical operator.")

  def evaluate_binary(self, expression):
    operator = expression.operator.type

    left = self.evaluate(expression.left)
    right = self.evaluate(expression.right)

    # Strict equality compares values without coercion.
    if operator == TokenType.STRICT_EQUAL:
        return self.strict_equal(left, right)

    if operator == TokenType.STRICT_NOT_EQUAL:
        return not self.strict_equal(left, right)

    # Arithmetic operators require numbers.
    if operator in (
        TokenType.PLUS,
        TokenType.MINUS,
        TokenType.STAR,
        TokenType.SLASH,
        TokenType.PERCENT,
    ):
        left = self.require_number(left, expression.operator)
        right = self.require_number(right, expression.operator)

        if operator == TokenType.PLUS:
            return left + right

        if operator == TokenType.MINUS:
            return left - right

        if operator == TokenType.STAR:
            return left * right

        if operator == TokenType.SLASH:
            return self.divide(left, right)

        if operator == TokenType.PERCENT:
            return self.remainder(left, right)

    # Comparisons also require numbers.
    left = self.require_number(left, expression.operator)
    right = self.require_number(right, expression.operator)

    if operator == TokenType.LESS:
        return left < right

    if operator == TokenType.LESS_EQUAL:
        return left <= right

    if operator == TokenType.GREATER:
        return left > right

    if operator == TokenType.GREATER_EQUAL:
        return left >= right

    raise InterpreterError("Unsupported binary operator.")

  # ==========================================
  # Numeric operations
  # ==========================================

  def require_number(self, value, operator):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InterpreterError(
            f"Operator '{operator.lexeme}' requires numeric operands."
        )

    return float(value)

  def divide(self, left, right):
    # JavaScript-style floating-point division by zero.
    if right != 0:
        return left / right

    if left == 0 or math.isnan(left):
        return math.nan

    # A nonzero number divided by +0 or -0.
    sign = math.copysign(1.0, left) * math.copysign(1.0, right)

    return math.copysign(math.inf, sign)

  def remainder(self, left, right):
    # JavaScript-style remainder has the sign of the dividend.
    if right == 0 or math.isnan(left) or math.isnan(right):
        return math.nan

    if math.isinf(left):
        return math.nan

    if math.isinf(right):
        return left

    if left == 0:
        return left

    return math.fmod(left, right)

  # ==========================================
  # Value handling
  # ==========================================

  def strict_equal(self, left, right):
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right

    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        if math.isnan(left) or math.isnan(right):
            return False

        return left == right

    return type(left) is type(right) and left == right

  def is_truthy(self, value):
    if value is False:
        return False

    if isinstance(value, float):
        if value == 0 or math.isnan(value):
            return False

    if isinstance(value, int) and not isinstance(value, bool):
        if value == 0:
            return False

    return True

  def stringify(self, value):
    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, float):
        if math.isnan(value):
            return "NaN"

        if math.isinf(value):
            return "Infinity" if value > 0 else "-Infinity"

        if value == 0:
            return "0"

        if value.is_integer():
            return str(int(value))

        return repr(value)

    return str(value)

