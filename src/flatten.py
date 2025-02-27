#!/usr/bin/env python3.10

from utils import *

def flatten(node):
    '''
    Recursive function that flattens an AST and converts complex expressions to simple single instructions.

    :param node: a node of the AST to flatten
    :return: a module that represents the equivalent Python representation to the AST
    '''
    if isinstance(node, Module):
        # intialize module to store temp assignments
        flatten.count = 0
        flatten.module = ast.parse("") 
        # flatten each statement in the module
        for x in node.body: flatten.module.body.append(flatten(x)) 
        return flatten.module
    elif isinstance(node, Assign):
        return Assign(
            targets=[flatten(x) for x in node.targets],
            value=flatten(node.value)
        )
    elif isinstance(node, Expr):
        return Expr(
            value=flatten(node.value)
        )
    elif isinstance(node, Constant):
        return node
    elif isinstance(node, Name):
        return node
    elif isinstance(node, BinOp):
        left = node.left
        right = node.right
        # if left operand is non-simple, flatten and store in temp variable
        if not isinstance(left, (Constant, Name)): 
            value = flatten(left)
            flatten.module.body.append(Assign(
                targets=[Name(
                    id=f"tmp{flatten.count}",
                    ctx=Store()
                )],
                value=value
            ))
            left = Name(
                id=f"tmp{flatten.count}",
                ctx=Load()
            )
            flatten.count += 1
        # if right operand is non-simple, flatten and store in temp variable
        if not isinstance(right, (Constant, Name)): 
            value = flatten(right)
            flatten.module.body.append(Assign(
                targets=[Name(
                    id=f"tmp{flatten.count}",
                    ctx=Store()
                )],
                value=value
            ))
            right = Name( 
                id=f"tmp{flatten.count}",
                ctx=Load()
            )
            flatten.count += 1
        return BinOp(
            left=left,
            op=node.op,
            right=right
        )
    elif isinstance(node, UnaryOp):
        operand = node.operand
        # if operand is non-simple, flatten and store in temp variable
        if not isinstance(operand, (Constant, Name)): 
            value = flatten(operand)
            flatten.module.body.append(Assign(
                targets=[Name(
                    id=f"tmp{flatten.count}",
                    ctx=Store()
                )],
                value=value
            ))
            operand = Name(
                id=f"tmp{flatten.count}",
                ctx=Load()
            )
            flatten.count += 1
        return UnaryOp(
            operand=operand,
            op=node.op
        )
    elif isinstance(node, Call):
        args = node.args
        for i in range(len(args)):
            if not isinstance(args[i], (Constant, Name)) and node.func.id != "eval":
                value = flatten(args[i])
                flatten.module.body.append(Assign(
                    targets=[Name(
                        id=f"tmp{flatten.count}",
                        ctx=Store()
                    )],
                    value=value
                ))
                args[i] = Name(
                    id=f"tmp{flatten.count}",
                    ctx=Load()
                )
                flatten.count += 1
        return Call(
            func=flatten(node.func),
            args=args,
            keywords=[]
        )
    elif isinstance(node, Add):
        return node
    elif isinstance(node, USub):
        return node
    elif isinstance(node, Load):
        return node
    elif isinstance(node, Store):
        return node
    else:
        raise Exception(f"flatten: unrecognized AST node {node}")
