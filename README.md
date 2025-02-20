# Python Subset Compiler

## Overview

This project is a compiler for a growing subset of Python, designed to parse, analyze, and execute Python code through incremental development. The goal is to gradually build a full compiler featuring a custom lexer and parser, support for user-defined classes and functions, control flow constructs such as conditionals and loops, and dynamic typing with variable scope management.

## Features

* **AST-based Parsing**  
  Uses Python's `ast` module to parse source code into an Abstract Syntax Tree for easy analysis and evaluation.

* **Unary Operations**  
  Supports unary minus operator (`-x`).

* **Binary Operations**  
  Supports binary addition (`x + y`).

* **Variables**  
  Allows defining and using variables through assignments and expressions.

* **Input and Output**  
  Supports `print()` statements for output and `eval(input())` for interactive input evaluation.

## Getting Started

### Requirements

* Python 3.10 or higher  
* x86 architecture

### Running the Compiler

* Build the runtime system:  
```bash
make -C runtime
```

* Build the compiler:
```bash
make
```

* Compile a program:
```bash
./pycomp your_program.py
```

* Link the generated assembly with the runtime system:
```bash
gcc -m32 -g your_program.s runtime/libpyyruntime.a -lm -o your_program
```

## Architecture

1. The source code is transformed into an abstract syntax tree (AST) using Python's `ast` library.
2. The AST is verified to be valid within the implemented subset.
3. Common tokens in the AST are made unique for easier manipulation.
4. Complex statements are flattened into simple statements within the AST.
5. The flattened AST is converted into Python code for intermediate validation.
6. The flattened AST is converted into x86 assembly.

## Examples

### py0

```python
# source
a = eval(input())
b = a + 10
print(-b)

# flattened
s_a = eval(input())
s_b = s_a + 10
tmp0 = - s_b
print(tmp0)

# input
7

# output
-17
```
