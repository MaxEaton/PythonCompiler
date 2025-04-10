#!/usr/bin/env python3.10

from utils import *

def declassify(node):
    '''
    Recursive function that converts classes within an AST into an object with external attribute assignments. 

    :param node: a node of the AST to declassify
    :return: a module that represents the equivalent Python representation to the AST with flattened classes
    '''
    global t_declassify_cnt
    if not hasattr(declassify, "map"):
        declassify.map = {}
    if not hasattr(declassify, "class_curr"):
        declassify.class_curr = None
        declassify.attributes = None
    if isinstance(node, Module):
        declassify.module = Module(body=[], type_ignores=[])
        for x in node.body: declassify.module.body.append(declassify(x))
        return declassify.module
    elif isinstance(node, Assign):
        if declassify.class_curr:
            if isinstance(node.targets[0], Name):
                declassify.attributes.add(node.targets[0].id)
            elif isinstance(node.targets[0], List):
                for elt in node.targets[0].elts:
                    declassify.attributes.add(elt)
        return Assign(
            targets=[declassify(target) for target in node.targets],
            value = declassify(node.value)
        )
    elif isinstance(node, Expr):
        return Expr(
            value=declassify(node.value)
        )
    elif isinstance(node, Name):
        if node.id in declassify.map:
            node.id = declassify.map[node.id]
        if declassify.attributes and node.id in declassify.attributes:
            return Attribute(
                value=Name(id=declassify.class_curr, ctx=Load()),
                attr=node.id,
                ctx=Load()
            )
        return node
    elif isinstance(node, (Constant, Pass, Break)):
        return node
    elif isinstance(node, BinOp):
        return BinOp(
            left=declassify(node.left),
            op=node.op,
            right=declassify(node.right)
        )
    elif isinstance(node, UnaryOp):
        return UnaryOp(
            operand=declassify(node.operand),
            op=node.op
        )
    elif isinstance(node, Call):
        return Call(
            func=declassify(node.func),
            args=[declassify(arg) for arg in node.args],
            keywords=[]
        )
    elif isinstance(node, BoolOp):
        return BoolOp(
            op=node.op,
            values=[declassify(value) for value in node.values]
        )
    elif isinstance(node, IfExp):
        return IfExp(
            test=declassify(node.test),
            body=declassify(node.body),
            orelse=declassify(node.orelse)
        )
    elif isinstance(node, Compare):
        return Compare(
            left=declassify(node.left),
            ops=node.ops,
            comparators=[declassify(c) for c in node.comparators]
        )
    elif isinstance(node, (If, While)):
        test = declassify(node.test)
        curr_module = declassify.module
        if_body = declassify(Module(body=node.body)).body
        or_body = declassify(Module(body=node.orelse)).body
        declassify.module = curr_module
        if isinstance(node, If): return If(test=test, body=if_body, orelse=or_body)
        elif isinstance(node, While): return While(test=test, body=if_body, orelse=or_body)
    elif isinstance(node, Subscript):
        return Subscript(
            value=declassify(node.value),
            slice=declassify(node.slice),
            ctx=node.ctx
        )
    elif isinstance(node, Dict):
        return Dict(
            keys=[declassify(key) for key in node.keys],
            values=[declassify(value) for value in node.values]
        )
    elif isinstance(node, List):
        return List(
            elts=[declassify(elt) for elt in node.elts],
            ctx=node.ctx
        )
    elif isinstance(node, Attribute):
        return Attribute(
            value=declassify(node.value),
            attr=node.attr,
            ctx=node.ctx
        )
    elif isinstance(node, Return):
        return Return(
            value=declassify(node.value)
        )
    elif isinstance(node, Lambda):
        return Lambda(
            args=node.args,
            body=declassify(node.body)
        )
    elif isinstance(node, FunctionDef):
        if node.name in declassify.map:
            node.name = declassify.map[node.name]
        curr_module = declassify.module
        class_curr = declassify.class_curr
        class_attributes = declassify.attributes
        declassify.class_curr = None
        declassify.attributes = None
        body = declassify(Module(body=node.body)).body
        declassify.module = curr_module
        declassify.class_curr = class_curr
        declassify.attributes = class_attributes
        declassify.module.body.append(FunctionDef(
            name=f"{declassify.class_curr+'_' if declassify.class_curr else ''}{node.name}",
            args=node.args,
            body=body
        ))
        if declassify.class_curr:
            declassify.attributes.add(node.name)
            return Assign(
                targets=[Attribute(
                    value=Name(id=declassify.class_curr, ctx=Load()),
                    attr=node.name,
                    ctx=Store()
                )],
                value=Name(
                    id=f"{declassify.class_curr+'_' if declassify.class_curr else ''}{node.name}", 
                    ctx=Load()
                )
            )
        return Pass()
    elif isinstance(node, ClassDef):
        class_prev = declassify.class_curr
        class_curr = f"t_class{t_declassify_cnt}"
        declassify.map[node.name] = class_curr
        declassify.class_curr = class_curr
        t_declassify_cnt += 1
        declassify.module.body.insert(0, ClassDef(
            name=class_curr,
            bases=[declassify(base) for base in node.bases],
            body=[Pass()]
        ))
        attributes_prev = declassify.attributes
        declassify.attributes = set()
        for x in node.body: declassify.module.body.append(declassify(x))
        declassify.class_curr = class_prev
        declassify.attributes = attributes_prev
        if declassify.class_curr:
            declassify.attributes.add(node.name)
            return Assign(
                targets=[Attribute(
                    value=Name(id=declassify.class_curr, ctx=Load()),
                    attr=node.name,
                    ctx=Store()
                )],
                value=Name(
                    id=f"{class_curr}", 
                    ctx=Load()
                )
            )
        return Assign(
            targets=[Name(id=node.name, ctx=Store())],
            value=Name(id=class_curr, ctx=Load())
        )
    else:
        raise Exception(f"declassify: unrecognized AST node {node}")
