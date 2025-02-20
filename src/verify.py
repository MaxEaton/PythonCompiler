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
    elif isinstance(node, Constant):
        pass
    elif isinstance(node, Name):
        node.id = f"s_{node.id}" if node.id not in functions else node.id
    elif isinstance(node, BinOp):
        verify(node.left)
        verify(node.op)
        verify(node.right)
    elif isinstance(node, UnaryOp):
        verify(node.operand)
        verify(node.op)
    elif isinstance(node, Call):
        # function must be print, eval, or input
        if node.func.id not in functions: 
            raise Exception(f"verify: unrecognized function {node.func.id}") 
        # no isolated inputs or evals
        if node.func.id == "eval" and (not len(node.args) or not isinstance(node.args[0], Call) or node.args[0].func.id != "input"): 
            raise Exception(f"verify: unrecognized isolated eval()")
        if node.func.id == "input":
            raise Exception(f"verify: unrecognized isolated input()")
        verify(node.func)
        # check to make sure there is not more than one argument
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
    elif isinstance(node, Add):
        pass
    elif isinstance(node, USub):
        pass
    elif isinstance(node, Load):
        pass
    elif isinstance(node, Store):
        pass
    else:
        raise Exception(f"verify: unrecognized AST node {node}")
