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

* **User Defined Classes**  
  Supports defining custom classes with bound and unbound methods, inheritance, and first-class support for class and function objects.  

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
3. Classes are flattened into instantiation followed by external attribute assignment. 
4. All variable names are made unique by prefixing with its parent scope. 
5. All lambdas and functions are unified into a closure and escaping variables are put on the heap. 
6. Logical operators are desugared into control blocks to support short circuiting and loops are desugared into infinite loops with a conditional break. 
7. Complex statements are flattened into simple statements within the AST.
8. The flattened AST is converted into Python code for intermediate validation.
9. The AST is converted into an IR that is then subdivided into a control flow graph (CFG). 
10. Overloaded operations are type checked at runtime to determine the appropriate operation to perform. 
11. Liveness analysis is performed and an interference graph is constructed. 
12. The interference graph is colored using a naive register allocation algorithm, and spill code is inserted as needed.  
13. The transformed program is converted into x86 assembly using the assigned register locations.

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

### py4

```python
# source
class A():
    x = 5
class B(A):
    y = 10
    def increment_by(self, z):
        self.x = self.x + z
    def get_sum(self):
        return self.x + self.y
o = B()
B.increment_by(o, eval(input()))
print(o.get_sum())

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
class Bound:
    def __init__(self, receiver, f):
        self.receiver = receiver
        self.f = f
def get_receiver(o):
    return o.receiver
def create_bound_method(receiver, f):
    return Bound(receiver, f)
class Unbound:
    def __init__(self, cl, f):
        self.cl = cl
        self.f = f
def get_class(o):
    return o.cl
def create_unbound_method(cl, f):
    return Unbound(cl, f)
def bind_methods(obj):
    cls = obj.__class__
    for attr in dir(cls):
        val = getattr(cls, attr)
        if isinstance(val, Unbound):
            bound = create_bound_method(obj, get_function(val))
            setattr(obj, attr, bound)
def get_function(o):
    return o.f
def caller(name, args):
    if isinstance(name, type):
        x = name(*args)
        bind_methods(x)
        return x
    elif isinstance(name, Closure):
        return name.get_fun_ptr()(name.get_free_vars(), *args)
    elif isinstance(name, Bound):
        f = get_function(name)
        return f.get_fun_ptr()(f.get_free_vars(), get_receiver(name), *args)
    elif isinstance(name, Unbound):
        f = get_function(name)
        return f.get_fun_ptr()(f.get_free_vars(), *args)

class s_t_class0():
    pass
class s_t_class1(s_t_class0):
    pass
def t_fun1(free_vars, arg_t_class1_increment_by_self, arg_t_class1_increment_by_z):
    t_flatten_0 = arg_t_class1_increment_by_self.x
    t_flatten_1 = t_flatten_0 + arg_t_class1_increment_by_z
    if isinstance(t_flatten_1, Closure):
        if isinstance(arg_t_class1_increment_by_self, type):
            arg_t_class1_increment_by_self.x = create_unbound_method(arg_t_class1_increment_by_self, t_flatten_1)
        else:
            arg_t_class1_increment_by_self.x = create_bound_method(arg_t_class1_increment_by_self, t_flatten_1)
    else:
        arg_t_class1_increment_by_self.x = t_flatten_1
def t_fun0(free_vars, arg_t_class1_get_sum_self):
    t_flatten_2 = arg_t_class1_get_sum_self.x
    t_flatten_3 = arg_t_class1_get_sum_self.y
    t_flatten_4 = t_flatten_2 + t_flatten_3
    return t_flatten_4
t_flatten_5 = []
t_flatten_6 = create_closure(t_fun0, t_flatten_5)
t_lambda1 = t_flatten_6
t_flatten_7 = []
t_flatten_8 = create_closure(t_fun1, t_flatten_7)
t_lambda0 = t_flatten_8
pass
pass
t_flatten_9 = 5
if isinstance(t_flatten_9, Closure):
    if isinstance(s_t_class0, type):
        s_t_class0.x = create_unbound_method(s_t_class0, t_flatten_9)
    else:
        s_t_class0.x = create_bound_method(s_t_class0, t_flatten_9)
else:
    s_t_class0.x = t_flatten_9
s_A = s_t_class0
t_flatten_10 = 10
if isinstance(t_flatten_10, Closure):
    if isinstance(s_t_class1, type):
        s_t_class1.y = create_unbound_method(s_t_class1, t_flatten_10)
    else:
        s_t_class1.y = create_bound_method(s_t_class1, t_flatten_10)
else:
    s_t_class1.y = t_flatten_10
s_t_class1_increment_by = t_lambda0
if isinstance(s_t_class1_increment_by, Closure):
    if isinstance(s_t_class1, type):
        s_t_class1.increment_by = create_unbound_method(s_t_class1, s_t_class1_increment_by)
    else:
        s_t_class1.increment_by = create_bound_method(s_t_class1, s_t_class1_increment_by)
else:
    s_t_class1.increment_by = s_t_class1_increment_by
s_t_class1_get_sum = t_lambda1
if isinstance(s_t_class1_get_sum, Closure):
    if isinstance(s_t_class1, type):
        s_t_class1.get_sum = create_unbound_method(s_t_class1, s_t_class1_get_sum)
    else:
        s_t_class1.get_sum = create_bound_method(s_t_class1, s_t_class1_get_sum)
else:
    s_t_class1.get_sum = s_t_class1_get_sum
s_B = s_t_class1
t_flatten_11 = caller(s_t_class1, [])
s_o = t_flatten_11
t_flatten_12 = s_t_class1.increment_by
t_flatten_13 = eval(input())
caller(t_flatten_12, [s_o, t_flatten_13])
t_flatten_14 = s_o.get_sum
t_flatten_15 = caller(t_flatten_14, [])
print(t_flatten_15)

# input
2

# output
17
```
