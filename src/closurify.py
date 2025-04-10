#!/usr/bin/env python3.10

from utils import *

def closurify(node):
    '''
    Converting function definitions into closures
    
    :param node: an AST node
    :return: set of free nodes
    '''
    global t_closurify_cnt
    if isinstance(node, Module):
        closurify.module = Module(body=[], type_ignores=[])
        for x in node.body: closurify.module.body.append(closurify(x))
        return closurify.module
    elif isinstance(node, Assign):
        return Assign(
            targets=node.targets,
            value=closurify(node.value)
        )
    elif isinstance(node, Expr):
        return Expr(
            value=closurify(node.value)
        )
    elif isinstance(node, (Constant, Name, Pass, Break)):
        return node
    elif isinstance(node, BinOp):
        return BinOp(
            left=closurify(node.left),
            op=node.op,
            right=closurify(node.right)
        )
    elif isinstance(node, UnaryOp):
        return UnaryOp(
            operand=closurify(node.operand),
            op=node.op
        )
    elif isinstance(node, Call):
        return Call(
            func=closurify(node.func),
            args=[closurify(arg) for arg in node.args],
            keywords=[]
        )
    elif isinstance(node, BoolOp):
        return BoolOp(
            op=node.op,
            values=[closurify(value) for value in node.values],
            keywords=[]
        )
    elif isinstance(node, IfExp):
        return IfExp(
            test=closurify(node.test),
            body=closurify(node.body),
            orelse=closurify(node.orelse),
        )
    elif isinstance(node, Compare):
        return Compare(
            left=closurify(node.left), 
            ops=node.ops, 
            comparators=[closurify(c) for c in node.comparators]
        )
    elif isinstance(node, If):
        return If(
            test=closurify(node.test),
            body=[closurify(x) for x in node.body],
            orelse=[closurify(x) for x in node.orelse],
        )
    elif isinstance(node, While):
        return While(
            test=closurify(node.test),
            body=[closurify(x) for x in node.body],
            orelse=[closurify(x) for x in node.orelse],
        )
    elif isinstance(node, Subscript):
        return Subscript(
            value=closurify(node.value),
            slice=closurify(node.slice),
            ctx=node.ctx
        )
    elif isinstance(node, Dict):
        return Dict(
            keys=[closurify(key) for key in node.keys],
            values=[closurify(value) for value in node.values]
        )
    elif isinstance(node, List):
        return List(
            elts=[closurify(elt) for elt in node.elts],
            ctx=node.ctx
        )
    elif isinstance(node, Attribute):
        return Attribute(
            value=closurify(node.value),
            attr=node.attr,
            ctx=node.ctx
        )
    elif isinstance(node, Return):
        return Return(
            value=closurify(node.value),
        )
    elif isinstance(node, FunctionDef):
        curr = t_closurify_cnt
        t_closurify_cnt += 1
        assignment = [
            Assign(
                targets=[Name(id=var, ctx=Store())],
                value=Subscript(
                    value=Name(id="free_vars", ctx=Load()),
                    slice=Constant(value=i),
                    ctx=Load()
                )
            )
            for i, var in enumerate(node.free)
        ]
        curr_module = closurify.module
        body = closurify(Module(body=node.body)).body
        closurify.module = curr_module
        node.args.args.insert(0, arg(arg="free_vars"))
        closurify.module.body.insert(0, FunctionDef(
            name=f"t_fun{curr}",
            args=node.args,
            body=[*assignment, *body]
        ))
        return Assign(
            targets=[Name(id=node.name, ctx=Store())],
            value=Call(
                func=Name(id=f"create_closure", ctx=Load()),
                args=[
                    Name(id=f"t_fun{curr}", ctx=Load()),
                    List(elts=[Name(id=id, ctx=Load()) for id in node.free], ctx=Load())
                ], 
                keywords=[]
            )
        )
    elif isinstance(node, ClassDef):
        closurify.module.body.insert(0, ClassDef(
            name=node.name,
            bases=[closurify(base) for base in node.bases],
            body=node.body,
        ))
        return Pass()
    else:
        raise Exception(f"closurify: unrecognized AST node {node}")
