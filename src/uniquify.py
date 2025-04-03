#!/usr/bin/env python3.10

from utils import *

def uniquify(node):
    global t_uniquify_cnt
    '''
    Recursive function that uniquifys program and returns AST with renamed variables. 

    :param node: node to uniquify
    :return: AST with uniquified variables
    '''
    if isinstance(node, Module):
        uniquify.scope = ""
        uniquify.mapper = {func: (func, False) for func in functions}
        for line in node.body: 
            if not isinstance(line, (Lambda, FunctionDef)): uniquify(line)
            else: uniquify.mapper[line.name] = (f"s_{uniquify.scope}{line.name}", False)
        for line in node.body: 
            if isinstance(line, (Lambda, FunctionDef)): uniquify(line)
        return node
    elif isinstance(node, Assign):
        for x in node.targets: uniquify(x)
        uniquify(node.value)
    elif isinstance(node, Expr):
        uniquify(node.value)
    elif isinstance(node, Name):
        if isinstance(node.ctx, Store):
            if node.id not in uniquify.mapper:
                uniquify.mapper[node.id] = (f"s_{uniquify.scope}{node.id}", False)
        elif node.id not in uniquify.mapper:
            uniquify.mapper[node.id] = (f"s_{uniquify.scope}{node.id}", True)
        node.id = uniquify.mapper[node.id][0]
    elif isinstance(node, BinOp):
        uniquify(node.left)
        uniquify(node.op)
        uniquify(node.right)
    elif isinstance(node, UnaryOp):
        uniquify(node.operand)
        uniquify(node.op)
    elif isinstance(node, Call):
        uniquify(node.func)
        for arg in node.args: uniquify(arg)
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
        for value in node.values: uniquify(value)
        uniquify(node.op)
    elif isinstance(node, IfExp):
        uniquify(node.test)
        uniquify(node.body)
        uniquify(node.orelse)
    elif isinstance(node, Compare):
        uniquify(node.left)
        for op in node.ops: uniquify(op)
        for comparator in node.comparators: uniquify(comparator)
    elif isinstance(node, (If, While)):
        uniquify(node.test)
        for line in node.body: uniquify(line)
        for line in node.orelse: uniquify(line)
    elif isinstance(node, Subscript):
        uniquify(node.value)
        uniquify(node.slice)
    elif isinstance(node, Dict):
        for key in node.keys: uniquify(key)
        for value in node.values: uniquify(value)
    elif isinstance(node, List):
        for elt in node.elts: uniquify(elt)
    elif isinstance(node, Return):
        uniquify(node.value)
    elif isinstance(node, Lambda):
        scope = uniquify.scope
        node.name = f"lambda{t_uniquify_cnt}"
        uniquify.mapper[node.name] = (f"s_{uniquify.scope}{node.name}", False)
        uniquify.scope += f"lambda{t_uniquify_cnt}_"
        node.name = f"s_{scope}{node.name}"
        mapper = dict(uniquify.mapper)
        t_uniquify_cnt += 1
        for i in range(len(node.args.args)):
            uniquify.mapper[node.args.args[i].arg] = (f"arg_{uniquify.scope}{node.args.args[i].arg}", True)
            node.args.args[i].arg = f"arg_{uniquify.scope}{node.args.args[i].arg}"
        uniquify(node.body)
        uniquify.mapper = mapper
        uniquify.scope = scope
    elif isinstance(node, FunctionDef):
        scope = uniquify.scope
        uniquify.mapper[node.name] = (f"s_{uniquify.scope}{node.name}", False)
        uniquify.scope += f"{node.name}_"
        node.name = f"s_{scope}{node.name}"
        mapper = dict(uniquify.mapper)
        for i in range(len(node.args.args)):
            uniquify.mapper[node.args.args[i].arg] = (f"arg_{uniquify.scope}{node.args.args[i].arg}", False)
            node.args.args[i].arg = f"arg_{uniquify.scope}{node.args.args[i].arg}"
        for line in node.body: 
            if not isinstance(line, FunctionDef): uniquify(line)
        for line in node.body: 
            if isinstance(line, FunctionDef): uniquify(line)
        uniquify.mapper = mapper
        uniquify.scope = scope
    elif isinstance(node, (Constant, Add, USub, Load, Store, And, Or, Not, Eq, NotEq, Is, Break)):
        pass
    else:
        raise Exception(f"uniquify: unrecognized AST node {node}")
