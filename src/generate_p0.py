#!/usr/bin/env python3.10

from utils import *

def generate_p0(node, indent):
    '''
    Recursive function that traverses an AST and converts it into its equivalent Python representation.

    :param node: a node of the AST
    :return: a string that represents the equivalent Python representation to the AST
    '''
    if isinstance(node, Module):
        return "\n".join([str(generate_p0(x, indent)) for x in node.body])
    elif isinstance(node, Assign):
        return f"{generate_p0(node.targets[0], indent)} = {generate_p0(node.value, indent)}"
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
        return f'{generate_p0(node.func, indent)}({",".join([str(generate_p0(x, indent)) for x in node.args])})'
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
    elif isinstance(node, Break):
        return "break"
    else:
        raise Exception(f"generate_p0: unrecognized AST node {node}")
