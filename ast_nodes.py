from dataclasses import dataclass
from typing import Union


@dataclass
class Literal:
    value: object


@dataclass
class Variable:
    name: str


@dataclass
class Unary:
    operator: object
    right: object


@dataclass
class Binary:
    left: object
    operator: object
    right: object


@dataclass
class Logical:
    left: object
    operator: object
    right: object

@dataclass
class LetStatement:
    name: str
    initializer: object


@dataclass
class Assignment:
    name: str
    value: object


@dataclass
class PrintStatement:
    expression: object


@dataclass
class Block:
    statements: list


@dataclass
class IfStatement:
    condition: object
    then_branch: Block
    else_branch: object = None


@dataclass
class WhileStatement:
    condition: object
    body: Block

