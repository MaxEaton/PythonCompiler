#!/usr/bin/env python3.10

from utils import *

def uniqify(node):
    '''
    Recursive function that converts variable names into unique names prefixed by its scope. 

    :param node: a node of the AST to uniqify
    :return: a module that has unique names for easier manipulations later
    '''
    global t_uniqify_cnt
    if isinstance(node, Module):
        uniqify.scope = ""
        uniqify.mapper = {func: (func, False) for func in functions}
        for line in node.body: 
            if not isinstance(line, (Lambda, FunctionDef)): uniqify(line)
            else: uniqify.mapper[line.name] = (f"s_{uniqify.scope}{line.name}", False)
        for line in node.body: 
            if isinstance(line, (Lambda, FunctionDef)): uniqify(line)
        return node
    elif isinstance(node, Assign):
        for x in node.targets: uniqify(x)
        uniqify(node.value)
    elif isinstance(node, Expr):
        uniqify(node.value)
    elif isinstance(node, Name):
        if isinstance(node.ctx, Store):
            if node.id not in uniqify.mapper:
                uniqify.mapper[node.id] = (f"s_{uniqify.scope}{node.id}", False)
        elif node.id not in uniqify.mapper:
            uniqify.mapper[node.id] = (f"s_{uniqify.scope}{node.id}", True)
        node.id = uniqify.mapper[node.id][0]
    elif isinstance(node, BinOp):
        uniqify(node.left)
        uniqify(node.op)
        uniqify(node.right)
    elif isinstance(node, UnaryOp):
        uniqify(node.operand)
        uniqify(node.op)
    elif isinstance(node, Call):
        uniqify(node.func)
        for arg in node.args: uniqify(arg)
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
        for value in node.values: uniqify(value)
        uniqify(node.op)
    elif isinstance(node, IfExp):
        uniqify(node.test)
        uniqify(node.body)
        uniqify(node.orelse)
    elif isinstance(node, Compare):
        uniqify(node.left)
        for op in node.ops: uniqify(op)
        for comparator in node.comparators: uniqify(comparator)
    elif isinstance(node, (If, While)):
        uniqify(node.test)
        for line in node.body: uniqify(line)
        for line in node.orelse: uniqify(line)
    elif isinstance(node, Subscript):
        uniqify(node.value)
        uniqify(node.slice)
    elif isinstance(node, Dict):
        for key in node.keys: uniqify(key)
        for value in node.values: uniqify(value)
    elif isinstance(node, List):
        for elt in node.elts: uniqify(elt)
    elif isinstance(node, Return):
        uniqify(node.value)
    elif isinstance(node, Lambda):
        scope = uniqify.scope
        node.name = f"lambda{t_uniqify_cnt}"
        uniqify.mapper[node.name] = (f"s_{uniqify.scope}{node.name}", False)
        uniqify.scope += f"lambda{t_uniqify_cnt}_"
        node.name = f"s_{scope}{node.name}"
        mapper = dict(uniqify.mapper)
        t_uniqify_cnt += 1
        for i in range(len(node.args.args)):
            uniqify.mapper[node.args.args[i].arg] = (f"arg_{uniqify.scope}{node.args.args[i].arg}", True)
            node.args.args[i].arg = f"arg_{uniqify.scope}{node.args.args[i].arg}"
        uniqify(node.body)
        uniqify.mapper = mapper
        uniqify.scope = scope
    elif isinstance(node, FunctionDef):
        scope = uniqify.scope
        uniqify.mapper[node.name] = (f"s_{uniqify.scope}{node.name}", False)
        uniqify.scope += f"{node.name}_"
        node.name = f"s_{scope}{node.name}"
        mapper = uniqify.mapper
        for i in range(len(node.args.args)):
            uniqify.mapper[node.args.args[i].arg] = (f"arg_{uniqify.scope}{node.args.args[i].arg}", False)
            node.args.args[i].arg = f"arg_{uniqify.scope}{node.args.args[i].arg}"
        for line in node.body: 
            if not isinstance(line, FunctionDef): uniqify(line)
        for line in node.body: 
            if isinstance(line, FunctionDef): uniqify(line)
        uniqify.mapper = mapper
        uniqify.scope = scope
    elif isinstance(node, Attribute):
        uniqify(node.value)
    elif isinstance(node, ClassDef):
        node.name = f"s_{uniqify.scope}{node.name}"
        for base in node.bases: uniqify(base)
    elif isinstance(node, (Constant, Add, USub, Load, Store, And, Or, Not, Eq, NotEq, Is, Pass, Break)):
        pass
    else:
        raise Exception(f"uniqify: unrecognized AST node {node}")
