import time

from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from compiler import BytecodeCompiler, execute_bytecode

# Generate a MiniJS program
ITERATIONS = 1_000_000

source = f"""
let i = 0;
let sum = 0;

while (i < {ITERATIONS}) {{
    sum = sum + i;
    i = i + 1;
}}

print(sum);
"""

# Lexing and parsing (common to both approaches)
tokens = Lexer(source).scan_tokens()
statements = Parser(tokens).parse()

# -----------------------------------
# 1. AST Interpreter
# -----------------------------------

ast_interpreter = Interpreter()

start = time.perf_counter()

for stmt in statements:
    ast_interpreter.execute(stmt)

ast_time = time.perf_counter() - start

# -----------------------------------
# 2. Bytecode Compilation
# -----------------------------------

compiler = BytecodeCompiler()

start = time.perf_counter()

code, max_regs = compiler.compile(statements)

compile_time = time.perf_counter() - start

# -----------------------------------
# 3. Bytecode Execution
# -----------------------------------

start = time.perf_counter()

execute_bytecode(code, max_regs)

vm_time = time.perf_counter() - start

# -----------------------------------
# Results
# -----------------------------------

print("\n========== BENCHMARK RESULTS ==========")

print(f"AST execution:       {ast_time:.6f} seconds")
print(f"Bytecode compilation: {compile_time:.6f} seconds")
print(f"Bytecode execution:   {vm_time:.6f} seconds")

total_vm_time = compile_time + vm_time

print(f"\nTotal bytecode time:  {total_vm_time:.6f} seconds")

if total_vm_time > 0:
    speedup = ast_time / total_vm_time
    print(f"Overall speedup:      {speedup:.2f}x")

print("=======================================")

