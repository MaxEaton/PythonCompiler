#!/usr/bin/env python3.10

from utils import *

def simplify(node):
    '''
    Converts an AST node into a simple expression

    :param node: an AST node to be simplified
    :return: a transformed AST node with simplified structure
    '''
    global t_flatten_cnt
    if isinstance(node, (Constant, Name, Break)): 
        return node
    else:
        # if not simple create new temporary variable and return
        value = flatten(node)
        flatten.module.body.append(Assign(
            targets=[Name(
                id=f"t_flatten_{t_flatten_cnt}",
                ctx=Store()
            )],
            value=value
        ))
        t_flatten_cnt += 1
        return Name(
            id=f"t_flatten_{t_flatten_cnt-1}",
            ctx=Load()
        )
    
def flatten(node):
    '''
    Recursive function that flattens an AST and converts complex expressions to simple single instructions.

    :param node: a node of the AST to flatten
    :return: a module that represents the equivalent Python representation to the AST
    '''
    if isinstance(node, Module):
        flatten.module = Module(body=[], type_ignores=[])
        for x in node.body: flatten.module.body.append(flatten(x))
        return flatten.module
    elif isinstance(node, Assign):
        return Assign(
            targets=[flatten(target) for target in node.targets],
            value=flatten(node.value)
        )
    elif isinstance(node, Expr):
        return Expr(
            value=flatten(node.value)
        )
    elif isinstance(node, (Constant, Name, Break)):
        return node
    elif isinstance(node, BinOp):
        return BinOp(
            left=simplify(node.left),
            op=node.op,
            right=simplify(node.right)
        )
    elif isinstance(node, UnaryOp):
        return UnaryOp(
            operand=simplify(node.operand),
            op=node.op
        )
    elif isinstance(node, Call):
        if node.func.id == "eval": 
            return node
        return Call(
            func=node.func,
            args=[simplify(arg) for arg in node.args],
            keywords=[]
        )
    elif isinstance(node, Compare):
        return Compare(
            left=simplify(node.left),
            ops=node.ops,
            comparators=[simplify(comparator) for comparator in node.comparators]
        )
    if isinstance(node, Subscript):
        return Subscript(
            value=simplify(node.value),
            slice=simplify(node.slice),
            ctx=node.ctx
        )
    if isinstance(node, Dict):
        return Dict(
            keys=[simplify(key) for key in node.keys],
            values=[simplify(value) for value in node.values]
        )
    if isinstance(node, List):
        return List(
            elts=[simplify(elt) for elt in node.elts],
            ctx=node.ctx
        )
    elif isinstance(node, (If, While)):
        # save current static module and create new submodules
        # revert to static module and return node with submodules 
        test = simplify(node.test)
        curr_module = flatten.module
        if_body = flatten(Module(body=node.body)).body
        or_body = flatten(Module(body=node.orelse)).body
        flatten.module = curr_module
        if isinstance(node, If): return If(test=test, body=if_body, orelse=or_body)
        elif isinstance(node, While): return While(test=test, body=if_body, orelse=or_body)
    else:
        raise Exception(f"flatten: unrecognized AST node {node}")
