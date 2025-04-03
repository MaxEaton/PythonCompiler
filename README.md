# Python Subset Compiler

## Overview

This project is a compiler for a growing subset of Python, designed to parse, analyze, and execute Python code through incremental development. The goal is to gradually build a full compiler featuring a custom lexer and parser, support for user-defined classes and functions, control flow constructs such as conditionals and loops, and dynamic typing with variable scope management.

## Features

* **Custom Parsing with Lark**  
  Uses Lark to implement a custom lexer and parser for the Python subset, enabling precise syntax control and incremental grammar development. 

* **Unary Operations**  
  Supports minus operator (`-x`) and not operator (`not x`).

* **Binary Operations**  
  Supports addition (`x + y`), logical operators (`x and/or y`) with short circuiting and comparison operators (`x ==/!=/is y`).

* **Ternary Operations**  
  Supports the ternary conditional expression (`x if y else z`) by desugaring it into an equivalent `if/else` statement.

* **Variables**  
Allows defining and using variables through assignments and expressions.

* **Input and Output**  
  Supports `print()` statements for output and `eval(input())` for interactive input evaluation.

* **Assigning Homes**  
  Implements liveness analysis and interference graph construction, followed by a basic graph coloring algorithm to allocate registers efficiently and minimize stack allocations. 

* **Basic Control**  
  Supports `if/else` statements and `while` loops, including support for `break` and `else` clauses within loops. 

* **Dynamic Typing**  
  Supports integers, booleans, lists, and dictionaries with runtime operator overloading based on operand types.

* **User Defined Functions**  
  Supports function definitions with proper scoping, and treats functions as first-class values that can be assigned, passed, and returned.

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

1. The source code is parsed using a custom grammar implemented with Lark, producing an abstract syntax tree.
2. The AST is verified to be valid within the implemented subset. 
3. All lambdas and functions are unified into a closure and escaping variables are put on the heap. 
4. Logical operators are desugared into control blocks to support short circuiting and loops are desugared into infinite loops with a conditional break. 
5. Complex statements are flattened into simple statements within the AST.
6. The flattened AST is converted into Python code for intermediate validation.
7. The AST is converted into an IR that is then subdivided into a control flow graph (CFG). 
8. Overloaded operations are type checked at runtime to determine the appropriate operation to perform. 
9. Liveness analysis is performed and an interference graph is constructed. 
10. The interference graph is colored using a naive register allocation algorithm, and spill code is inserted as needed.  
11. The transformed program is converted into x86 assembly using the assigned register locations.

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

### py1

```python
# source
x = eval(input())
y = eval(input())
while x and y:
    print(-x if int(x == y) else y)
    x = x + -1
    y = y + -2

# flattened
s_x = eval(input())
s_y = eval(input())
while 1:
    t_desugar_1 = s_x
    if t_desugar_1:
        t_desugar_2 = s_y
    else:
        t_desugar_2 = t_desugar_1
    t_desugar_0 = t_desugar_2
    if t_desugar_0:
        t_flatten_0 = int(s_x == s_y)
        if t_flatten_0:
            t_desugar_3 = - s_x
        else:
            t_desugar_3 = s_y
        print(t_desugar_3)
        t_flatten_1 = - 1
        s_x = s_x + t_flatten_1
        t_flatten_2 = - 2
        s_y = s_y + t_flatten_2
    else:
        break

# input
5
6

# output
6
-4
2
```

### py2

```python
# source
m = eval(input())
n = 3
l1 = [{}, 1, False, 4]
l2 = [[3]]
l3 = l1 + l2
print(l3[m+n])

# flattened
s_m = eval(input())
s_n = 3
t_flatten_0 = {}
s_l1 = [t_flatten_0, 1, False, 4]
t_flatten_1 = [3]
s_l2 = [t_flatten_1]
s_l3 = s_l1 + s_l2
t_flatten_2 = s_m + s_n
t_flatten_3 = s_l3[t_flatten_2]
print(t_flatten_3)

# input
True

# output
[3]
```

### py3

```python
# source
y = 3
def f(x):
    return lambda: y + x
print(f(2)())
y = eval(input())
print(f(2)())

# flattened
class Closure:
    def __init__(self, fun_ptr, free_vars):
        self.fun_ptr = fun_ptr
        self.free_vars = free_vars
    def get_fun_ptr(self):
        return self.fun_ptr
    def get_free_vars(self):
        return self.free_vars
def create_closure(fun_ptr, free_vars):
    return Closure(fun_ptr, free_vars)

def t_fun0(free_vars, arg_f_x):
    t_flatten_0 = 0
    s_y = free_vars[t_flatten_0]
    def t_fun1(free_vars):
        t_flatten_1 = 0
        s_y = free_vars[t_flatten_1]
        t_flatten_2 = 1
        arg_f_x = free_vars[t_flatten_2]
        t_flatten_3 = 0
        t_flatten_4 = s_y[t_flatten_3]
        t_flatten_5 = 0
        t_flatten_6 = arg_f_x[t_flatten_5]
        t_flatten_7 = t_flatten_4 + t_flatten_6
        return t_flatten_7
    arg_f_x = [arg_f_x]
    t_flatten_8 = [s_y, arg_f_x]
    t_lambda1 = create_closure(t_fun1, t_flatten_8)
    return t_lambda1
t_flatten_9 = 0
s_y = [t_flatten_9]
t_flatten_10 = [s_y]
t_lambda0 = create_closure(t_fun0, t_flatten_10)
t_flatten_11 = 0
t_flatten_12 = 3
s_y[t_flatten_11] = t_flatten_12
s_f = t_lambda0
t_flatten_13 = 2
t_flatten_14 = s_f(t_flatten_13) if s_f in [print, int] else s_f.get_fun_ptr()(s_f.get_free_vars(), t_flatten_13)
t_flatten_15 = t_flatten_14() if t_flatten_14 in [print, int] else t_flatten_14.get_fun_ptr()(t_flatten_14.get_free_vars())
print(t_flatten_15) if print in [print, int] else print.get_fun_ptr()(print.get_free_vars(), t_flatten_15)
t_flatten_16 = 0
s_y[t_flatten_16] = eval(input())
t_flatten_17 = 2
t_flatten_18 = s_f(t_flatten_17) if s_f in [print, int] else s_f.get_fun_ptr()(s_f.get_free_vars(), t_flatten_17)
t_flatten_19 = t_flatten_18() if t_flatten_18 in [print, int] else t_flatten_18.get_fun_ptr()(t_flatten_18.get_free_vars())
print(t_flatten_19) if print in [print, int] else print.get_fun_ptr()(print.get_free_vars(), t_flatten_19)

# input
1

# output
5
3
```
