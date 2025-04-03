#!/usr/bin/env python3.10

from utils import *

def unify(node):
    """
    Unify lambdas and functions and place at the top of the module for easier processing
    
    :param node: an AST node
    :return: an AST node
    """
    global t_unify_cnt
    if isinstance(node, Module):
        unify.module = Module(body=[], type_ignores=[])
        for x in node.body: unify.module.body.append(unify(x))
        return unify.module
    elif isinstance(node, Assign):
        return Assign(
            targets=node.targets,
            value = unify(node.value)
        )
    elif isinstance(node, Expr):
        return Expr(
            value=unify(node.value)
        )
    elif isinstance(node, (Constant, Name, Break)):
        return node
    elif isinstance(node, BinOp):
        return BinOp(
            left=unify(node.left),
            op=node.op,
            right=unify(node.right)
        )
    elif isinstance(node, UnaryOp):
        return UnaryOp(
            operand=unify(node.operand),
            op=node.op
        )
    elif isinstance(node, Call):
        return Call(
            func=unify(node.func),
            args=[unify(arg) for arg in node.args],
            keywords=[]
        )
    elif isinstance(node, BoolOp):
        return BoolOp(
            values=[unify(value) for value in node.values],
            op=node.op
        )
    elif isinstance(node, IfExp):
        return IfExp(
            test=unify(node.test),
            body=unify(node.body),
            orelse=unify(node.orelse)
        )
    elif isinstance(node, Compare):
        return Compare(
            left=unify(node.left), 
            ops=node.ops, 
            comparators=[unify(c) for c in node.comparators]
        )
    elif isinstance(node, If):
        return If(
            test=unify(node.test),
            body=[unify(line) for line in node.body],
            orelse=[unify(line) for line in node.orelse]
        )
    elif isinstance(node, While):
        return While(
            test=unify(node.test),
            body=[unify(line) for line in node.body],
            orelse=[unify(line) for line in node.orelse]
        )
    elif isinstance(node, Subscript):
        return Subscript(
            value=unify(node.value),
            slice=unify(node.slice),
            ctx=node.ctx
        )
    elif isinstance(node, Dict):
        return Dict(
            keys=[unify(key) for key in node.keys],
            values=[unify(value) for value in node.values]
        )
    elif isinstance(node, List):
        return List(
            elts=[unify(elt) for elt in node.elts],
            ctx=node.ctx
        )
    elif isinstance(node, Return):
        return Return(
            value=unify(node.value),
        )
    elif isinstance(node, Lambda):
        curr = t_unify_cnt
        t_unify_cnt += 1
        curr_module = unify.module
        body = unify(Module(body=[Return(value=node.body)])).body
        unify.module = curr_module
        # insert lambda function as a function at beginning of module
        unify.module.body.insert(0, FunctionDef( 
            name=f"t_lambda{curr}",
            args=node.args,
            body=body
        ))
        return Name(
            id=f"t_lambda{curr}",
            ctx=Load()
        )
    elif isinstance(node, FunctionDef):
        curr = t_unify_cnt
        t_unify_cnt += 1
        curr_module = unify.module
        body = unify(Module(body=node.body)).body
        unify.module = curr_module
        # insert function as a function at beginning of module
        unify.module.body.insert(0, FunctionDef( 
            name=f"t_lambda{curr}",
            args=node.args,
            body=body
        ))
        return Assign(
            targets=[Name(id=node.name, ctx=Store())],
            value=Name(id=f"t_lambda{curr}", ctx=Load())
        )
    else:
        raise Exception(f"desugar: unrecognized AST node {node}")
