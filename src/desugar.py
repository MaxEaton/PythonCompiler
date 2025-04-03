#!/usr/bin/env python3.10

from utils import *

def t_desugar():
    '''
    Generates a new temporary variable for desugaring transformations.

    :return: an instance of Name representing the new t_desug variable
    '''
    global t_desugar_cnt
    name = Name(id=f"t_desugar_{t_desugar_cnt}", ctx=Store())
    t_desugar_cnt += 1
    return name

def desugar(node):
    '''
    Performs desugaring transformations on an AST node.

    :param node: an AST node to be transformed
    :return: a desugared AST node
    '''
    if isinstance(node, Module):
        # create new static module for desugared nodes to be added to and return
        desugar.module = Module(body=[], type_ignores=[])
        for x in node.body: desugar.module.body.append(desugar(x))
        return desugar.module
    elif isinstance(node, Assign):
        return Assign(
            targets=node.targets,
            value = desugar(node.value)
        )
    elif isinstance(node, Expr):
        return Expr(
            value=desugar(node.value)
        )
    elif isinstance(node, (Constant, Name, Break)):
        return node
    elif isinstance(node, BinOp):
        return BinOp(
            left=desugar(node.left),
            op=node.op,
            right=desugar(node.right)
        )
    elif isinstance(node, UnaryOp):
        return UnaryOp(
            operand=desugar(node.operand),
            op=node.op
        )
    elif isinstance(node, Call):
        return Call(
            func=node.func,
            args=[desugar(arg) for arg in node.args],
            keywords=[]
        )
    elif isinstance(node, BoolOp):
        # save current static module and create new submodules
        # add If node with submodules to module and revert to static module
        # return destination module for easy assignment
        test = t_desugar()
        dest = t_desugar()
        curr_module = desugar.module
        curr_module.body.extend(desugar(Module(body=[Assign(targets=[test],value=node.values[0])])).body)
        if isinstance(node.op, Or):
            body = [Assign(targets=[dest],value=test)]
            orelse = desugar(Module(body=[Assign(targets=[dest],value=node.values[1])])).body
        elif isinstance(node.op, And):
            body = desugar(Module(body=[Assign(targets=[dest],value=node.values[1])])).body
            orelse = [Assign(targets=[dest],value=test)]
        curr_module.body.append(If(test=test, body=body, orelse=orelse))
        desugar.module = curr_module
        return dest
    elif isinstance(node, IfExp):
        # save current static module and create new submodules
        # add If node with submodules to module and revert to static module
        # return destination module for easy assignment
        test = desugar(node.test)
        dest = t_desugar()
        curr_module = desugar.module
        body = desugar(Module(body=[Assign(targets=[dest],value=node.body)])).body
        orelse = desugar(Module(body=[Assign(targets=[dest],value=node.orelse)])).body
        curr_module.body.append(If(test=test, body=body, orelse=orelse))
        desugar.module = curr_module
        return dest
    elif isinstance(node, Compare):
        return Compare(
            left=desugar(node.left), 
            ops=node.ops, 
            comparators=[desugar(c) for c in node.comparators]
        )
    elif isinstance(node, If):
        # save current static module and create new submodules
        # revert to static module and return If node with submodules 
        test = desugar(node.test)
        curr_module = desugar.module
        body = desugar(Module(body=node.body)).body
        orelse = desugar(Module(body=node.orelse)).body
        desugar.module = curr_module
        return If(test=test, body=body, orelse=orelse)
    elif isinstance(node, While):
        # save current static module and create new submodules
        # convert to infinite loop with internal else case including a break and return
        test = t_desugar()
        curr_module = desugar.module
        testing = desugar(Module(body=[Assign(targets=[test],value=node.test)])).body
        body = desugar(Module(body=node.body)).body
        orelse = desugar(Module(body=node.orelse)).body
        desugar.module = curr_module
        return While(
            test=Constant(value=1), 
            body=[*testing, If(test=test, body=body, orelse=[*orelse, Break()])], 
            orelse=[]
        )
    elif isinstance(node, Subscript):
        return Subscript(
            value=desugar(node.value),
            slice=desugar(node.slice),
            ctx=node.ctx
        )
    elif isinstance(node, Dict):
        return Dict(
            keys=[desugar(key) for key in node.keys],
            values=[desugar(value) for value in node.values]
        )
    elif isinstance(node, List):
        return List(
            elts=[desugar(elt) for elt in node.elts],
            ctx=node.ctx
        )
    elif isinstance(node, Return):
        return Return(
            value=desugar(node.value),
        )
    elif isinstance(node, FunctionDef):
        curr_module = desugar.module
        body = desugar(Module(body=node.body)).body
        desugar.module = curr_module
        return FunctionDef(
            name=node.name,
            args=node.args,
            body=body
        )
    else:
        raise Exception(f"desugar: unrecognized AST node {node}")
