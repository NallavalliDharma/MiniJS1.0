from dataclasses import dataclass
# Python provides a module called dataclasses
# A dataclass helps you create classes whose primary purpose is to store data.
# dataclass to define a token as a structured data object without manually writing common methods such as its constructor and default representation.

from enum import Enum,auto 

# Enum allows us to define a fixed collection of named values.

# auto() automatically assigns a value to an enumeration member.
# Enum defines a fixed set of token types, and auto() assigns their values automatically.
class TokenType(Enum):
    # Keywords
    LET = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    TRUE = auto()
    FALSE = auto()
    PRINT = auto()

    # Identifiers and numbers
    IDENTIFIER = auto()
    NUMBER = auto()

    # Arithmetic operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()

    # Comparison operators
    LESS = auto()
    LESS_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()

    # Equality operators
    STRICT_EQUAL = auto()
    STRICT_NOT_EQUAL = auto()

    # Logical operators
    NOT = auto()
    AND = auto()
    OR = auto()

    # Assignment
    EQUAL = auto()

    # Punctuation
    SEMICOLON = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()

    # End of source
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    lexeme: str
    literal: object = None
    line: int = 1          

    def __repr__(self):
        return (
            f"Token(type={self.type.name},"
            f"lexeme={self.lexeme!r}, "
            f"literal={self.literal!r}, "
            f"line={self.line})"
        )

