#!/usr/bin/env python3.10

from utils import *

def uniqify(node):
    '''
    Recursively makes each node unique to distinguish common tokens. 

    :param node: a node of the AST to uniqify
    :return: unqified AST
    '''
    if isinstance(node, Module):
        return Module(
            body=[uniqify(x) for x in node.body],
            type_ignores=[]
        )
    elif isinstance(node, Assign):
        return Assign(
            targets=[uniqify(x) for x in node.targets],
            value=uniqify(node.value)
        )
    elif isinstance(node, Expr):
        return Expr(
            value=uniqify(node.value)
        )
    elif isinstance(node, Constant):
        return node
    elif isinstance(node, Name):
        return Name(
            id=node.id,
            ctx=uniqify(node.ctx)
        )
    elif isinstance(node, BinOp):
        return BinOp(
            left=uniqify(node.left),
            op=uniqify(node.op),
            right=uniqify(node.right),
        )
    elif isinstance(node, UnaryOp):
        return UnaryOp(
            operand=uniqify(node.operand),
            op=uniqify(node.op),
        )
    elif isinstance(node, Call):
        return Call(
            func=uniqify(node.func),
            args=[uniqify(x) for x in node.args],
            keywords=[]
        )
    elif isinstance(node, Add):
        return Add()
    elif isinstance(node, USub):
        return USub()
    elif isinstance(node, Load):
        return Load()
    elif isinstance(node, Store):
        return Store()
    else:
        raise Exception(f"uniqify: unrecognized AST node {node}")
