import sys
from pathlib import Path

from lexer import Lexer
from parser import Parser, ParseError
from interpreter import Interpreter, InterpreterError

def run_file(file_path):
  """Read, parse, and execute a MiniJS source file."""


  path = Path(file_path)

  # Step 1: Read the source file.
  try:
      source = path.read_text(encoding="utf-8")
  except OSError as error:
      print(f"Error: Cannot read source file: {error}", file=sys.stderr)
      return 1

  # Step 2: Tokenize the complete source.
  try:
      tokens = Lexer(source).scan_tokens()
  except SyntaxError as error:
      print(f"Lexical error: {error}", file=sys.stderr)
      return 1

  # Step 3: Parse the complete source before execution.
  try:
      statements = Parser(tokens).parse()
  except ParseError as error:
      print(f"Syntax error: {error}", file=sys.stderr)
      return 1

  # Step 4: Execute only after lexing and parsing succeed.
  interpreter = Interpreter()

  try:
      interpreter.interpret(statements)
  except (InterpreterError, RuntimeError) as error:
      print(f"Runtime error: {error}", file=sys.stderr)
      return 1
  except Exception as error:
      print(f"Runtime error: {error}", file=sys.stderr)
      return 1

  return 0


def main():
  """Validate command-line arguments and run one source file."""
  
  if len(sys.argv) != 2:
      print(
          "Usage: python main.py <source-file>",
          file=sys.stderr,
      )
      return 1
  return run_file(sys.argv[1])
if __name__ == "__main__":
  sys.exit(main())
