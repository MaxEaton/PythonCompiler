#!/usr/bin/env python3.10

from utils import *

def s_ir(tree):
    '''
    Takes flattened AST and returns assembly ir.

    :param tree: root of AST
    :return: list of assembly ir
    '''
    def call(func, args):
        name = None
        if func.id == "print":
            name = "print_int_nl"
        elif func.id == "eval":
            name = "eval_input_int"
        else:
            raise Exception(f"s_ir.call: unrecognized function {func.id}")
        arg = None
        if isinstance(args[0], Constant):
            arg = args[0].value
        elif isinstance(args[0], Name):
            arg = args[0].id
        return ["call", name, arg]
    
    def assign(node, dest):
        if isinstance(node, Constant):
            return [["movl", node.value, dest]]
        elif isinstance(node, Name):
            return [["movl", node.id, dest]]
        elif isinstance(node, BinOp):
            left = right = None
            if isinstance(node.left, Constant):
                left = node.left.value
            elif isinstance(node.left, Name):
                left = node.left.id
            if isinstance(node.right, Constant):
                right = node.right.value
            elif isinstance(node.right, Name):
                right = node.right.id
            return [
                ["movl", left, dest],
                ["addl", right, dest],
            ]
        elif isinstance(node, UnaryOp):
            operand = None
            if isinstance(node.operand, Constant):
                operand = node.operand.value
            elif isinstance(node.operand, Name):
                operand = node.operand.id
            return [
                ["movl", operand, dest],
                ["negl", dest],
            ]
        elif isinstance(node, Call):
            return [
                call(node.func, node.args), 
                ["movl", "%eax", dest],
            ]
        else:
            raise Exception(f"s_ir: unrecognized AST node {node}")
        
    if not isinstance(tree, Module):
        raise Exception(f"s_ir: unrecognized AST node {node}")
    
    s_ir_arr = []
        
    for node in tree.body:
        if isinstance(node, Assign):
            s_ir_arr.extend(assign(node.value, node.targets[0].id))
        elif isinstance(node, Expr):
            if isinstance(node.value, Call):
                s_ir_arr.append(call(node.value.func, node.value.args))
        else:
            raise Exception(f"s_ir: unrecognized AST node {node}")
    
    return s_ir_arr
