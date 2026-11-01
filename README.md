# MiniJS 1.0 – High-Performance Execution Engine

An independent execution engine for the MiniJS 1.0 programming language, built using Python. It features lexical analysis, recursive-descent parsing, a register-based bytecode compiler, and a custom virtual machine (VM).

## Features

* **Lexical Analysis:** Converts MiniJS source code into tokens.
* **Recursive-Descent Parser:** Parses tokens and generates an Abstract Syntax Tree (AST).
* **Bytecode Compiler:** Converts AST nodes into register-based bytecode instructions.
* **Virtual Machine:** Executes compiled bytecode using a custom instruction dispatch loop.
* **Immediate Optimizations:** Uses optimized instructions for operations involving numeric constants.
* **Short-Circuit Evaluation:** Supports logical `&&` and `||` operations.
* **Lexical Scoping:** Supports nested blocks, variable shadowing, and scope management.
* **Runtime Error Handling:** Handles undefined variables, duplicate declarations, and temporal dead zone errors.

## Project Structure

```text
MiniJS/
│
├── main.py           # CLI entry point
├── tokens.py         # Token definitions
├── lexer.py          # Lexical analyzer
├── ast_nodes.py      # AST node definitions
├── parser.py         # Recursive-descent parser
├── compiler.py       # Bytecode compiler and virtual machine
├── interpreter.py    # Coordinates bytecode execution
├── environment.py    # Variable and scope management
├── benchmark.py      # Performance benchmark
└── README.md
```

## Requirements

* Python 3.x

No external dependencies are required.

## Run the Interpreter

Create a MiniJS source file, for example `program.mjs`.

Run it using:

```bash
python main.py program.mjs
```

## Example Program

```javascript
let i = 0;
let sum = 0;

while (i < 1000000) {
    sum = sum + i;
    i = i + 1;
}

print(sum);
```

**Output:**

```text
499999500000
```

## Run Correctness Tests

If you have the `correctness_test.py` file, run:

```bash
python correctness_test.py -- python main.py
```

## Performance Benchmark

The bytecode engine was benchmarked using a program that calculates the sum of numbers from `0` to `999,999`.

The benchmark was executed five times.

| Run         | Compilation Time (s) | Execution Time (s) | Total Time (s) |
| ----------- | -------------------: | -----------------: | -------------: |
| 1           |             0.000033 |           0.498893 |       0.498926 |
| 2           |             0.000055 |           0.525187 |       0.525243 |
| 3           |             0.000052 |           0.541532 |       0.541584 |
| 4           |             0.000048 |           0.506414 |       0.506462 |
| 5           |             0.000053 |           0.566965 |       0.567017 |
| **Average** |         **0.000048** |       **0.527798** |   **0.527846** |

**Average total execution time: 0.527846 seconds.**

All five benchmark runs produced the expected output:

```text
499999500000
```

## Technologies Used

* Python
* Data Structures and Algorithms
* Compiler Design
* Lexical Analysis
* Recursive-Descent Parsing
* Register-Based Bytecode
* Virtual Machine Design
