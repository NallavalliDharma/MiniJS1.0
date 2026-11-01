"""Bytecode Compiler and Virtual Machine for MiniJS 1.0.

Provides high-performance execution of MiniJS abstract syntax trees.
Compiles AST statements into flat register-based bytecode instructions
and executes them in a specialized virtual machine loop.
"""

import math
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

UNINITIALIZED = object()

# Bytecode opcodes
(
    OP_ADD,
    OP_ADD_RC,
    OP_LT_RC,
    OP_JUMP_IF_FALSE,
    OP_JUMP,
    OP_SUB,
    OP_SUB_RC,
    OP_MUL,
    OP_MUL_RC,
    OP_LT,
    OP_LE_RC,
    OP_LE,
    OP_GT_RC,
    OP_GT,
    OP_GE_RC,
    OP_GE,
    OP_EQ,
    OP_NEQ,
    OP_CONST,
    OP_MOVE,
    OP_PRINT,
    OP_DECLARE,
    OP_INITIALIZE,
    OP_CHECK_INIT,
    OP_UNDEFINED_READ,
    OP_UNDEFINED_ASSIGN,
    OP_REDECLARE_ERROR,
    OP_JUMP_IF_TRUE,
    OP_DIV_RC,
    OP_DIV,
    OP_MOD_RC,
    OP_MOD,
    OP_NEG,
    OP_POS,
    OP_NOT,
) = range(35)


class CompileScope:
    def __init__(self, parent=None):
        self.parent = parent
        self.variables = {}  # name -> reg_slot

    def declare(self, name, slot):
        if name in self.variables:
            return False
        self.variables[name] = slot
        return True

    def resolve(self, name):
        scope = self
        while scope is not None:
            if name in scope.variables:
                return scope.variables[name]
            scope = scope.parent
        return None


class BytecodeCompiler:
    def __init__(self):
        self.instructions = []
        self.next_reg = 0
        self.current_scope = CompileScope()
        self.scope_init_vars = set()

    def alloc_reg(self):
        r = self.next_reg
        self.next_reg += 1
        return r

    def emit(self, op, *args):
        idx = len(self.instructions)
        self.instructions.append((op, *args))
        return idx

    def patch_jump(self, idx, target_pc):
        old = self.instructions[idx]
        self.instructions[idx] = (old[0], *old[1:-1], target_pc)

    def compile(self, statements):
        for stmt in statements:
            self.compile_statement(stmt)
        return self.instructions, self.next_reg

    def compile_to_reg(self, expr):
        if isinstance(expr, Variable):
            slot = self.current_scope.resolve(expr.name)
            if slot is None:
                r = self.alloc_reg()
                self.emit(OP_UNDEFINED_READ, expr.name)
                return r
            if slot not in self.scope_init_vars:
                self.emit(OP_CHECK_INIT, slot, expr.name)
            return slot
        r = self.alloc_reg()
        self.compile_expression(expr, r)
        return r

    def compile_statement(self, stmt):
        if isinstance(stmt, LetStatement):
            if stmt.name in self.current_scope.variables:
                self.emit(OP_REDECLARE_ERROR, stmt.name)
                temp = self.alloc_reg()
                self.compile_expression(stmt.initializer, temp)
                return

            slot = self.alloc_reg()
            self.current_scope.declare(stmt.name, slot)
            self.emit(OP_DECLARE, slot)
            self.compile_expression(stmt.initializer, slot)
            self.emit(OP_INITIALIZE, slot)
            self.scope_init_vars.add(slot)

        elif isinstance(stmt, Assignment):
            slot = self.current_scope.resolve(stmt.name)
            if slot is None:
                temp = self.alloc_reg()
                self.compile_expression(stmt.value, temp)
                self.emit(OP_UNDEFINED_ASSIGN, stmt.name)
            else:
                if slot not in self.scope_init_vars:
                    self.emit(OP_CHECK_INIT, slot, stmt.name)
                self.compile_expression(stmt.value, slot)

        elif isinstance(stmt, PrintStatement):
            r = self.alloc_reg()
            self.compile_expression(stmt.expression, r)
            self.emit(OP_PRINT, r)

        elif isinstance(stmt, Block):
            self.compile_block(stmt)

        elif isinstance(stmt, IfStatement):
            cond_reg = self.alloc_reg()
            self.compile_expression(stmt.condition, cond_reg)
            jump_false = self.emit(OP_JUMP_IF_FALSE, cond_reg, -1)
            self.compile_block(stmt.then_branch)
            if stmt.else_branch is not None:
                jump_end = self.emit(OP_JUMP, -1)
                self.patch_jump(jump_false, len(self.instructions))
                self.compile_block(stmt.else_branch)
                self.patch_jump(jump_end, len(self.instructions))
            else:
                self.patch_jump(jump_false, len(self.instructions))

        elif isinstance(stmt, WhileStatement):
            loop_start = len(self.instructions)
            cond_reg = self.alloc_reg()
            self.compile_expression(stmt.condition, cond_reg)
            jump_end = self.emit(OP_JUMP_IF_FALSE, cond_reg, -1)
            self.compile_block(stmt.body)
            self.emit(OP_JUMP, loop_start)
            self.patch_jump(jump_end, len(self.instructions))

        else:
            raise RuntimeError(f"Unknown statement: {stmt}")

    def compile_block(self, block):
        prev_scope = self.current_scope
        self.current_scope = CompileScope(parent=prev_scope)

        for s in block.statements:
            self.compile_statement(s)

        self.current_scope = prev_scope

    def compile_expression(self, expr, dst_reg):
        if isinstance(expr, Literal):
            val = expr.value
            if type(val) is int and type(val) is not bool:
                val = float(val)
            self.emit(OP_CONST, dst_reg, val)

        elif isinstance(expr, Variable):
            slot = self.current_scope.resolve(expr.name)
            if slot is None:
                self.emit(OP_UNDEFINED_READ, expr.name)
            else:
                if slot not in self.scope_init_vars:
                    self.emit(OP_CHECK_INIT, slot, expr.name)
                if dst_reg != slot:
                    self.emit(OP_MOVE, dst_reg, slot)

        elif isinstance(expr, Unary):
            src_reg = self.alloc_reg()
            self.compile_expression(expr.right, src_reg)
            op_type = expr.operator.type
            if op_type == TokenType.NOT:
                self.emit(OP_NOT, dst_reg, src_reg)
            elif op_type == TokenType.MINUS:
                self.emit(OP_NEG, dst_reg, src_reg)
            elif op_type == TokenType.PLUS:
                self.emit(OP_POS, dst_reg, src_reg)
            else:
                raise RuntimeError(f"Unknown unary operator: {op_type}")

        elif isinstance(expr, Binary):
            if (
                isinstance(expr.right, Literal)
                and type(expr.right.value) in (int, float)
                and type(expr.right.value) is not bool
            ):
                const_val = float(expr.right.value)
                left_reg = self.compile_to_reg(expr.left)
                op_type = expr.operator.type
                if op_type == TokenType.PLUS:
                    self.emit(OP_ADD_RC, dst_reg, left_reg, const_val)
                    return
                elif op_type == TokenType.MINUS:
                    self.emit(OP_SUB_RC, dst_reg, left_reg, const_val)
                    return
                elif op_type == TokenType.STAR:
                    self.emit(OP_MUL_RC, dst_reg, left_reg, const_val)
                    return
                elif op_type == TokenType.SLASH:
                    self.emit(OP_DIV_RC, dst_reg, left_reg, const_val)
                    return
                elif op_type == TokenType.PERCENT:
                    self.emit(OP_MOD_RC, dst_reg, left_reg, const_val)
                    return
                elif op_type == TokenType.LESS:
                    self.emit(OP_LT_RC, dst_reg, left_reg, const_val)
                    return
                elif op_type == TokenType.LESS_EQUAL:
                    self.emit(OP_LE_RC, dst_reg, left_reg, const_val)
                    return
                elif op_type == TokenType.GREATER:
                    self.emit(OP_GT_RC, dst_reg, left_reg, const_val)
                    return
                elif op_type == TokenType.GREATER_EQUAL:
                    self.emit(OP_GE_RC, dst_reg, left_reg, const_val)
                    return

            left_reg = self.compile_to_reg(expr.left)
            right_reg = self.compile_to_reg(expr.right)
            op_type = expr.operator.type
            if op_type == TokenType.PLUS:
                self.emit(OP_ADD, dst_reg, left_reg, right_reg)
            elif op_type == TokenType.MINUS:
                self.emit(OP_SUB, dst_reg, left_reg, right_reg)
            elif op_type == TokenType.STAR:
                self.emit(OP_MUL, dst_reg, left_reg, right_reg)
            elif op_type == TokenType.SLASH:
                self.emit(OP_DIV, dst_reg, left_reg, right_reg)
            elif op_type == TokenType.PERCENT:
                self.emit(OP_MOD, dst_reg, left_reg, right_reg)
            elif op_type == TokenType.LESS:
                self.emit(OP_LT, dst_reg, left_reg, right_reg)
            elif op_type == TokenType.LESS_EQUAL:
                self.emit(OP_LE, dst_reg, left_reg, right_reg)
            elif op_type == TokenType.GREATER:
                self.emit(OP_GT, dst_reg, left_reg, right_reg)
            elif op_type == TokenType.GREATER_EQUAL:
                self.emit(OP_GE, dst_reg, left_reg, right_reg)
            elif op_type == TokenType.STRICT_EQUAL:
                self.emit(OP_EQ, dst_reg, left_reg, right_reg)
            elif op_type == TokenType.STRICT_NOT_EQUAL:
                self.emit(OP_NEQ, dst_reg, left_reg, right_reg)
            else:
                raise RuntimeError(f"Unknown binary operator: {op_type}")

        elif isinstance(expr, Logical):
            op_type = expr.operator.type
            if op_type == TokenType.OR:
                self.compile_expression(expr.left, dst_reg)
                jump_idx = self.emit(OP_JUMP_IF_TRUE, dst_reg, -1)
                self.compile_expression(expr.right, dst_reg)
                self.patch_jump(jump_idx, len(self.instructions))
            elif op_type == TokenType.AND:
                self.compile_expression(expr.left, dst_reg)
                jump_idx = self.emit(OP_JUMP_IF_FALSE, dst_reg, -1)
                self.compile_expression(expr.right, dst_reg)
                self.patch_jump(jump_idx, len(self.instructions))
            else:
                raise RuntimeError(f"Unknown logical operator: {op_type}")

        else:
            raise RuntimeError(f"Unknown expression: {expr}")


def stringify_value(value):
    if type(value) is bool:
        return "true" if value else "false"
    if type(value) is float:
        if value != value:
            return "NaN"
        if math.isinf(value):
            return "Infinity" if value > 0 else "-Infinity"
        if value == 0.0:
            return "0"
        if value.is_integer() and abs(value) <= 9007199254740992:
            return str(int(value))
        return repr(value)
    return str(value)


def execute_bytecode(code, max_regs):
    regs = [UNINITIALIZED] * max_regs
    pc = 0
    code_len = len(code)

    while pc < code_len:
        ins = code[pc]
        op = ins[0]

        # Hot loop operations ordered first for maximum dispatch speed
        if op == OP_ADD:
            a = regs[ins[2]]
            b = regs[ins[3]]
            if type(a) is not float or type(b) is not float:
                raise RuntimeError("Operator '+' requires numeric operands.")
            regs[ins[1]] = a + b
            pc += 1

        elif op == OP_ADD_RC:
            a = regs[ins[2]]
            if type(a) is not float:
                raise RuntimeError("Operator '+' requires numeric operands.")
            regs[ins[1]] = a + ins[3]
            pc += 1

        elif op == OP_LT_RC:
            a = regs[ins[2]]
            if type(a) is not float:
                raise RuntimeError("Operator '<' requires numeric operands.")
            regs[ins[1]] = a < ins[3]
            pc += 1

        elif op == OP_JUMP_IF_FALSE:
            val = regs[ins[1]]
            if val is False or val == 0.0 or val != val:
                pc = ins[2]
            else:
                pc += 1

        elif op == OP_JUMP:
            pc = ins[1]

        elif op == OP_SUB:
            a = regs[ins[2]]
            b = regs[ins[3]]
            if type(a) is not float or type(b) is not float:
                raise RuntimeError("Operator '-' requires numeric operands.")
            regs[ins[1]] = a - b
            pc += 1

        elif op == OP_SUB_RC:
            a = regs[ins[2]]
            if type(a) is not float:
                raise RuntimeError("Operator '-' requires numeric operands.")
            regs[ins[1]] = a - ins[3]
            pc += 1

        elif op == OP_MUL:
            a = regs[ins[2]]
            b = regs[ins[3]]
            if type(a) is not float or type(b) is not float:
                raise RuntimeError("Operator '*' requires numeric operands.")
            regs[ins[1]] = a * b
            pc += 1

        elif op == OP_MUL_RC:
            a = regs[ins[2]]
            if type(a) is not float:
                raise RuntimeError("Operator '*' requires numeric operands.")
            regs[ins[1]] = a * ins[3]
            pc += 1

        elif op == OP_LT:
            a = regs[ins[2]]
            b = regs[ins[3]]
            if type(a) is not float or type(b) is not float:
                raise RuntimeError("Operator '<' requires numeric operands.")
            regs[ins[1]] = a < b
            pc += 1

        elif op == OP_LE_RC:
            a = regs[ins[2]]
            if type(a) is not float:
                raise RuntimeError("Operator '<=' requires numeric operands.")
            regs[ins[1]] = a <= ins[3]
            pc += 1

        elif op == OP_LE:
            a = regs[ins[2]]
            b = regs[ins[3]]
            if type(a) is not float or type(b) is not float:
                raise RuntimeError("Operator '<=' requires numeric operands.")
            regs[ins[1]] = a <= b
            pc += 1

        elif op == OP_CONST:
            regs[ins[1]] = ins[2]
            pc += 1

        elif op == OP_MOVE:
            regs[ins[1]] = regs[ins[2]]
            pc += 1

        elif op == OP_PRINT:
            print(stringify_value(regs[ins[1]]))
            pc += 1

        elif op == OP_DECLARE:
            regs[ins[1]] = UNINITIALIZED
            pc += 1

        elif op == OP_INITIALIZE:
            pc += 1

        elif op == OP_CHECK_INIT:
            if regs[ins[1]] is UNINITIALIZED:
                raise RuntimeError(f"Cannot access '{ins[2]}' before initialization.")
            pc += 1

        elif op == OP_UNDEFINED_READ:
            raise RuntimeError(f"Undefined variable '{ins[1]}'.")

        elif op == OP_UNDEFINED_ASSIGN:
            raise RuntimeError(f"Undefined variable '{ins[1]}'.")

        elif op == OP_REDECLARE_ERROR:
            raise RuntimeError(f"Variable '{ins[1]}' is already declared in this scope.")

        elif op == OP_JUMP_IF_TRUE:
            val = regs[ins[1]]
            if val is not False and val != 0.0 and val == val:
                pc = ins[2]
            else:
                pc += 1

        elif op == OP_DIV_RC:
            a = regs[ins[2]]
            b = ins[3]
            if type(a) is not float:
                raise RuntimeError("Operator '/' requires numeric operands.")
            if b != 0.0:
                regs[ins[1]] = a / b
            elif a == 0.0 or a != a:
                regs[ins[1]] = math.nan
            else:
                sign = math.copysign(1.0, a) * math.copysign(1.0, b)
                regs[ins[1]] = math.copysign(math.inf, sign)
            pc += 1

        elif op == OP_DIV:
            a = regs[ins[2]]
            b = regs[ins[3]]
            if type(a) is not float or type(b) is not float:
                raise RuntimeError("Operator '/' requires numeric operands.")
            if b != 0.0:
                regs[ins[1]] = a / b
            elif a == 0.0 or a != a:
                regs[ins[1]] = math.nan
            else:
                sign = math.copysign(1.0, a) * math.copysign(1.0, b)
                regs[ins[1]] = math.copysign(math.inf, sign)
            pc += 1

        elif op == OP_MOD_RC:
            a = regs[ins[2]]
            b = ins[3]
            if type(a) is not float:
                raise RuntimeError("Operator '%' requires numeric operands.")
            if b == 0.0 or a != a or b != b or math.isinf(a):
                regs[ins[1]] = math.nan
            elif math.isinf(b) or a == 0.0:
                regs[ins[1]] = a
            else:
                regs[ins[1]] = math.fmod(a, b)
            pc += 1

        elif op == OP_MOD:
            a = regs[ins[2]]
            b = regs[ins[3]]
            if type(a) is not float or type(b) is not float:
                raise RuntimeError("Operator '%' requires numeric operands.")
            if b == 0.0 or a != a or b != b or math.isinf(a):
                regs[ins[1]] = math.nan
            elif math.isinf(b) or a == 0.0:
                regs[ins[1]] = a
            else:
                regs[ins[1]] = math.fmod(a, b)
            pc += 1

        elif op == OP_NEG:
            a = regs[ins[2]]
            if type(a) is not float:
                raise RuntimeError("Operator '-' requires numeric operands.")
            regs[ins[1]] = -a
            pc += 1

        elif op == OP_POS:
            a = regs[ins[2]]
            if type(a) is not float:
                raise RuntimeError("Operator '+' requires numeric operands.")
            regs[ins[1]] = +a
            pc += 1

        elif op == OP_NOT:
            val = regs[ins[2]]
            regs[ins[1]] = (val is False or val == 0.0 or val != val)
            pc += 1

        elif op == OP_GT_RC:
            a = regs[ins[2]]
            if type(a) is not float:
                raise RuntimeError("Operator '>' requires numeric operands.")
            regs[ins[1]] = a > ins[3]
            pc += 1

        elif op == OP_GT:
            a = regs[ins[2]]
            b = regs[ins[3]]
            if type(a) is not float or type(b) is not float:
                raise RuntimeError("Operator '>' requires numeric operands.")
            regs[ins[1]] = a > b
            pc += 1

        elif op == OP_GE_RC:
            a = regs[ins[2]]
            if type(a) is not float:
                raise RuntimeError("Operator '>=' requires numeric operands.")
            regs[ins[1]] = a >= ins[3]
            pc += 1

        elif op == OP_GE:
            a = regs[ins[2]]
            b = regs[ins[3]]
            if type(a) is not float or type(b) is not float:
                raise RuntimeError("Operator '>=' requires numeric operands.")
            regs[ins[1]] = a >= b
            pc += 1

        elif op == OP_EQ:
            a = regs[ins[2]]
            b = regs[ins[3]]
            if type(a) is not type(b):
                regs[ins[1]] = False
            elif type(a) is float:
                regs[ins[1]] = False if (a != a or b != b) else (a == b)
            else:
                regs[ins[1]] = (a == b)
            pc += 1

        elif op == OP_NEQ:
            a = regs[ins[2]]
            b = regs[ins[3]]
            if type(a) is not type(b):
                regs[ins[1]] = True
            elif type(a) is float:
                regs[ins[1]] = True if (a != a or b != b) else (a != b)
            else:
                regs[ins[1]] = (a != b)
            pc += 1

        else:
            raise RuntimeError(f"Unknown opcode: {op}")
