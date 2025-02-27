#!/usr/bin/env python3.10

from utils import *

def generate_p0(node):
    '''
    Recursive function that traverses an AST and converts it into its equivalent Python representation.

    :param node: a node of the AST
    :return: a string that represents the equivalent Python representation to the AST
    '''
    if isinstance(node, Module):
        return "\n".join([str(generate_p0(x)) for x in node.body])
    elif isinstance(node, Assign):
        return f"{generate_p0(node.targets[0])} = {generate_p0(node.value)}"
    elif isinstance(node, Expr):
        return generate_p0(node.value)
    elif isinstance(node, Constant):
        return node.value
    elif isinstance(node, Name):
        return node.id
    elif isinstance(node, BinOp):
        return f"{generate_p0(node.left)} {generate_p0(node.op)} {generate_p0(node.right)}"
    elif isinstance(node, UnaryOp):
        return f"{generate_p0(node.op)} {generate_p0(node.operand)}"
    elif isinstance(node, Call):
        return f'{generate_p0(node.func)}({",".join([str(generate_p0(x)) for x in node.args])})'
    elif isinstance(node, Add):
        return "+"
    elif isinstance(node, USub):
        return "-"
    elif isinstance(node, Load):
        return ""
    elif isinstance(node, Store):
        return ""
    else:
        raise Exception(f"generate_p0: unrecognized AST node {node}")
