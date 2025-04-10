#!/usr/bin/env python3.10

from utils import *

def generate_p0(node, indent):
    '''
    Recursive function that traverses an AST and converts it into its equivalent Python representation.

    :param node: a node of the AST
    :return: a string that represents the equivalent Python representation to the AST
    '''
    if isinstance(node, Module):
        header = (
            "class Closure:\n"
            "    def __init__(self, fun_ptr, free_vars):\n"
            "        self.fun_ptr = fun_ptr\n"
            "        self.free_vars = free_vars\n"
            "    def get_fun_ptr(self):\n"
            "        return self.fun_ptr\n"
            "    def get_free_vars(self):\n"
            "        return self.free_vars\n"
            "def create_closure(fun_ptr, free_vars):\n"
            "    return Closure(fun_ptr, free_vars)\n"
            "class Bound:\n"
            "    def __init__(self, receiver, f):\n"
            "        self.receiver = receiver\n"
            "        self.f = f\n"
            "def get_receiver(o):\n"
            "    return o.receiver\n"
            "def create_bound_method(receiver, f):\n"
            "    return Bound(receiver, f)\n"
            "class Unbound:\n"
            "    def __init__(self, cl, f):\n"
            "        self.cl = cl\n"
            "        self.f = f\n"
            "def get_class(o):\n"
            "    return o.cl\n"
            "def create_unbound_method(cl, f):\n"
            "    return Unbound(cl, f)\n"
            "def bind_methods(obj):\n"
            "    cls = obj.__class__\n"
            "    for attr in dir(cls):\n"
            "        val = getattr(cls, attr)\n"
            "        if isinstance(val, Unbound):\n"
            "            bound = create_bound_method(obj, get_function(val))\n"
            "            setattr(obj, attr, bound)\n"
            "def get_function(o):\n"
            "    return o.f\n"
            "def caller(name, args):\n"
            "    if isinstance(name, type):\n"
            "        x = name(*args)\n"
            "        bind_methods(x)\n"
            "        return x\n"
            "    elif isinstance(name, Closure):\n"
            "        return name.get_fun_ptr()(name.get_free_vars(), *args)\n"
            "    elif isinstance(name, Bound):\n"
            "        f = get_function(name)\n"
            "        return f.get_fun_ptr()(f.get_free_vars(), get_receiver(name), *args)\n"
            "    elif isinstance(name, Unbound):\n"
            "        f = get_function(name)\n"
            "        return f.get_fun_ptr()(f.get_free_vars(), *args)\n"
            "\n"
        )
        return header + "\n".join([str(generate_p0(x, indent)) for x in node.body])
    elif isinstance(node, Assign):
        target = generate_p0(node.targets[0], indent)
        value = generate_p0(node.value, indent)
        if isinstance(node.targets[0], Attribute):
            obj = generate_p0(node.targets[0].value, indent)
            return (
                f"if isinstance({value}, Closure):\n"
                f"{' '*indent*4}    if isinstance({obj}, type):\n"
                f"{' '*indent*4}        {target} = create_unbound_method({obj}, {value})\n"
                f"{' '*indent*4}    else:\n"
                f"{' '*indent*4}        {target} = create_bound_method({obj}, {value})\n"
                f"{' '*indent*4}else:\n"
                f"{' '*indent*4}    {target} = {value}"
            )
        return f"{target} = {value}"
    elif isinstance(node, Expr):
        return generate_p0(node.value, indent)
    elif isinstance(node, Constant):
        return f"\"{node.value}\"" if isinstance(node.value, str) else str(node.value)
    elif isinstance(node, Name):
        return node.id
    elif isinstance(node, BinOp):
        return f"{generate_p0(node.left, indent)} {generate_p0(node.op, indent)} {generate_p0(node.right, indent)}"
    elif isinstance(node, UnaryOp):
        return f"{generate_p0(node.op, indent)} {generate_p0(node.operand, indent)}"
    elif isinstance(node, Call):
        if isinstance(node.func, Name) and node.func.id == "eval": return "eval(input())"
        if isinstance(node.func, Name) and node.func.id == "create_closure": return f'{generate_p0(node.func, indent)}({", ".join([str(generate_p0(x, indent)) for x in node.args])})'
        if isinstance(node.func, Name) and node.func.id == "print": return f"print({generate_p0(node.args[0], indent)})"
        if isinstance(node.func, Name) and node.func.id == "int": return f"int({generate_p0(node.args[0], indent)})"
        caller = generate_p0(node.func, indent)
        if '.' in caller:
            obj = caller.split('.')[0]
            return f'caller({caller}, [{", ".join([obj]+[str(generate_p0(x, indent)) for x in node.args])}])'
        return f'caller({generate_p0(node.func, indent)}, [{", ".join([str(generate_p0(x, indent)) for x in node.args])}])'
    elif isinstance(node, Compare):
        return f"{str(generate_p0(node.left, indent))} {str(generate_p0(node.ops[0], indent))} {str(generate_p0(node.comparators[0], indent))}"
    elif isinstance(node, (If, While)):
        result = "if " if isinstance(node, If) else "while "
        result += f"{generate_p0(node.test, 0)}:\n" + \
                  f"{' ' * (indent+1) * 4}" + \
                  f"\n{' ' * (indent+1) * 4}".join([str(generate_p0(x, indent+1)) for x in node.body])
        if node.orelse:
            result += f"\n{' ' * (indent) * 4}else:\n" + \
                      f"{' ' * (indent+1) * 4}" + \
                      f"\n{' ' * (indent+1) * 4}".join([str(generate_p0(x, indent+1)) for x in node.orelse])
        return result
    elif isinstance(node, Subscript):
        if isinstance(node.slice, Constant): value = node.slice.value
        else: value = node.slice.id
        return f"{node.value.id}[{value}]"
    elif isinstance(node, Dict):
        return f"{{{', '.join([f'{generate_p0(k, indent)}: {generate_p0(v, indent)}' for k, v in zip(node.keys, node.values)])}}}"
    elif isinstance(node, List):
        return f"[{', '.join([generate_p0(elt, indent) for elt in node.elts])}]"
    elif isinstance(node, Attribute):
        return f"{generate_p0(node.value, indent)}.{node.attr}"
    elif isinstance(node, FunctionDef):
        result = f"def {node.name}({', '.join(arg.arg for arg in node.args.args)}):\n" + \
                 f"{' ' * (indent+1) * 4}" + \
                 f"\n{' ' * (indent+1) * 4}".join([str(generate_p0(x, indent+1)) for x in node.body])
        return result
    elif isinstance(node, ClassDef):
        return f"class {node.name}({', '.join([generate_p0(base, indent) for base in node.bases])}):\n" + \
                 f"{' ' * (indent+1) * 4}" + \
                 f"\n{' ' * (indent+1) * 4}".join([str(generate_p0(x, indent+1)) for x in node.body])
    elif isinstance(node, Add):
        return "+"
    elif isinstance(node, USub):
        return "-"
    elif isinstance(node, Not):
        return "not"
    elif isinstance(node, Eq):
        return "=="
    elif isinstance(node, NotEq):
        return "!="
    elif isinstance(node, Is):
        return "is"
    elif isinstance(node, (Load, Store)):
        return ""
    elif isinstance(node, Pass):
        return "pass"
    elif isinstance(node, Break):
        return "break"
    elif isinstance(node, Return):
        return f"return {str(generate_p0(node.value, indent))}"
    else:
        raise Exception(f"generate_p0: unrecognized AST node {node}")
