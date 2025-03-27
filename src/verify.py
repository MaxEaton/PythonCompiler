#!/usr/bin/env python3.10


from utils import *


def verify(node):
    '''
    Recursive function that verifys program to be p0 and returns AST with renamed variables. 

    :param node: node to verify
    :return: AST if verified p0 program
    '''
    if isinstance(node, Module):
        for x in node.body: verify(x)
        return node
    elif isinstance(node, Assign):
        for x in node.targets: verify(x)
        verify(node.value)
    elif isinstance(node, Expr):
        verify(node.value)
    elif isinstance(node, Name):
        node.id = f"s_{node.id}" if node.id not in [*functions, *keywords] else node.id
    elif isinstance(node, BinOp):
        verify(node.left)
        verify(node.op)
        verify(node.right)
    elif isinstance(node, UnaryOp):
        verify(node.operand)
        verify(node.op)
    elif isinstance(node, Call):
        if node.func.id not in functions: 
            # function must be print, eval, or input
            raise Exception(f"verify: unrecognized function {node.func.id}") 
        if node.func.id == "eval" and (not len(node.args) or not isinstance(node.args[0], Call) or node.args[0].func.id != "input"): 
            # no isolated eval
            raise Exception(f"verify: unrecognized isolated eval()")
        if node.func.id == "input":
            # no isolated input
            raise Exception(f"verify: unrecognized isolated input()")
        verify(node.func)
        # check to make sure there isn't more than one argument
        if node.func.id != "eval": 
            if len(node.args) > 1:
                raise Exception(f"verify: too many arguments {node.func.id}")
            for x in node.args: verify(x)
        else:
            if len(node.args[0].args):
                if len(node.args[0].args) == 1:
                    verify(node.args[0].args[0])
                else:
                    raise Exception(f"verify: too many arguments {node.args[0].func.id}")
    elif isinstance(node, BoolOp):
        if len(node.values) > 2:
            values = node.values[1:]
            node.values = [
                node.values[0],
                BoolOp(
                    op=node.op,
                    values=values
                )
            ]
        for value in node.values: verify(value)
        verify(node.op)
    elif isinstance(node, IfExp):
        verify(node.test)
        verify(node.body)
        verify(node.orelse)
    elif isinstance(node, Compare):
        verify(node.left)
        for op in node.ops: verify(op)
        for comparator in node.comparators: verify(comparator)
    elif isinstance(node, (If, While)):
        verify(node.test)
        for line in node.body: verify(line)
        for line in node.orelse: verify(line)
    elif isinstance(node, Subscript):
        verify(node.value)
        verify(node.slice)
    elif isinstance(node, Dict):
        for key in node.keys: verify(key)
        for value in node.values: verify(value)
    elif isinstance(node, List):
        for elt in node.elts: verify(elt)
    elif isinstance(node, (Constant, Add, USub, Load, Store, And, Or, Not, Eq, NotEq, Is, Break)):
        pass
    else:
        raise Exception(f"verify: unrecognized AST node {node}")
