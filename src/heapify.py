#!/usr/bin/env python3.10

from utils import *

def name_of(node):
    '''
    Finds name of given function or variable

    :param node: an AST node
    :return: a node name or node value
    '''
    if isinstance(node, Name):
        return node.id
    return name_of(node.value)

def heapify(node, free=None, heap=None):
    '''
    Transforms an AST to use heap-allocated variables for free variables.

    :param node: an AST node
    :param free: a set of free variables
    :param heap: a set of heaped variables
    :return: an AST
    '''
    global t_heapify_cnt
    if isinstance(node, Module):
        heapify.free = free
        heapify.heap = heap
        # initalize each heap variable
        heapify.module = Module(body=[ 
            Assign(
                targets=[Name(id=var, ctx=Store())],
                value=List(elts=[Name(id=var, ctx=Load()) if var.startswith("arg_") else Constant(value=0)], ctx=Load())
            )
            for var in heapify.heap
        ], type_ignores=[])
        # heapify all free variables
        for x in node.body: heapify.module.body.append(heapify(x))
        return heapify.module
    elif isinstance(node, Assign):
        # convert heap assignment to subscripted assignment
        if name_of(node.targets[0]) in heapify.heap: 
            return Assign(
                targets=[Subscript(
                    value=node.targets[0],
                    slice=Constant(value=0),
                    ctx=Store()
                )],
                value=heapify(node.value)
            )
        return Assign(
            targets=[heapify(node.targets[0])],
            value=heapify(node.value)
        )
    elif isinstance(node, Expr):
        return Expr(
            value=heapify(node.value)
        )
    elif isinstance(node, (Constant, Break)):
        return node
    elif isinstance(node, Name):
        if node.id in heapify.free | heapify.heap:
            return Subscript(
                value=node,
                slice=Constant(value=0),
                ctx=Load()
            )
        return node
    elif isinstance(node, BinOp):
        return BinOp(
            left=heapify(node.left),
            op=node.op,
            right=heapify(node.right)
        )
    elif isinstance(node, UnaryOp):
        return UnaryOp(
            operand=heapify(node.operand),
            op=node.op
        )
    elif isinstance(node, Call):
        return Call(
            func=heapify(node.func),
            args=[heapify(arg) for arg in node.args],
            keywords=[]
        )
    elif isinstance(node, BoolOp):
        return BoolOp(
            op=node.op,
            values=[heapify(value) for value in node.values]
        )
    elif isinstance(node, IfExp):
        return IfExp(
            test=heapify(node.test),
            body=heapify(node.body),
            orelse=heapify(node.orelse)
        )
    elif isinstance(node, Compare):
        return Compare(
            left=heapify(node.left), 
            ops=node.ops, 
            comparators=[heapify(c) for c in node.comparators]
        )
    elif isinstance(node, If):
        return If(
            test=heapify(node.test),
            body=[heapify(c) for c in node.body],
            orelse=[heapify(c) for c in node.orelse]
        )
    elif isinstance(node, While):
        return While(
            test=heapify(node.test),
            body=[heapify(c) for c in node.body],
            orelse=[heapify(c) for c in node.orelse]
        )
    elif isinstance(node, Subscript):
        return Subscript(
            value=heapify(node.value),
            slice=heapify(node.slice),
            ctx=node.ctx
        )
    elif isinstance(node, Dict):
        return Dict(
            keys=[heapify(key) for key in node.keys],
            values=[heapify(value) for value in node.values]
        )
    elif isinstance(node, List):
        return List(
            elts=[heapify(elt) for elt in node.elts],
            ctx=node.ctx
        )
    elif isinstance(node, Return):
        return Return(
            value=heapify(node.value)
        )
    elif isinstance(node, FunctionDef):
        curr_heap = set(heapify.heap)
        curr_module = heapify.module
        body = heapify(Module(body=node.body), node.free, node.heap).body
        heapify.heap = curr_heap
        heapify.module = curr_module
        # rewrite function definition with new parameters
        return FunctionDef( 
            name=node.name,
            args=node.args,
            body=body,
            free=node.free,
            heap=node.heap
        )
    else:
        raise Exception(f"heapify: unrecognized AST node {node}")
