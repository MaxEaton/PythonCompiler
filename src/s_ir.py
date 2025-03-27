#!/usr/bin/env python3.10

from utils import *

def s_ir(tree):
    '''
    Takes flattened AST and returns assembly ir.

    :param tree: root of AST
    :return: list of assembly ir
    '''
    global if_cnt, while_cnt, while_depth, t_ir_cnt
    
    def value(node):
        # return node value based on type
        if isinstance(node, Constant): return node.value
        elif isinstance(node, Name): return node.id
        elif isinstance(node, Subscript): return (value(node.value), value(node.slice))
        raise Exception(f"s_ir: unrecognized AST node {node}")
    
    def call(func, args):
        # map function and add args
        name_map = {
            "print": "print_any",
            "eval": "eval_input_pyobj",
            "int": "int",
        }
        name = name_map.get(func.id)
        if not name:
            raise Exception(f"s_ir.call: unrecognized function {func.id}")
        args = [] if name == "eval_input_pyobj" else [value(arg) for arg in args]
        if name == "int": 
            return [
                ["call", "project_bool", args],
                ["call", "inject_int", ["%eax"]],
            ]
        return [["call", name, args]]
    
    def ifelse(test, body, orelse):
        # perform test and sandwhich between jumps and labels
        global if_cnt
        cnt = if_cnt
        if_cnt += 1
        return [
            ["call", "is_true", [value(test)]],
            ["cmpl", 0, "%eax"],
            ["je", f"ifelse{cnt}"],
            [f"ifthen{cnt}"],
            *s_ir(Module(body=body)),
            ["jmp", f"ifend{cnt}"],
            [f"ifelse{cnt}"],
            *s_ir(Module(body=orelse)),
            [f"ifend{cnt}"]
        ]
        
    def while_loop(body):
        # record depth for break and revert
        # sanwhich interior with jumps and labels
        global while_cnt, while_depth
        cnt = while_cnt
        prv = while_depth
        while_depth = cnt
        while_cnt += 1
        ret = [
            [f"while_loop{cnt}"],
            *s_ir(Module(body=body)),
            ["jmp", f"while_loop{cnt}"],
            [f"while_end{cnt}"],
        ]
        while_depth = prv
        return ret
    
    def assign(node, dest):
        # perform operations based on IR
        if isinstance(node, (Constant, Name)):
            return [["movl", value(node), dest]]
        elif isinstance(node, BinOp):
            left = value(node.left)
            right = value(node.right)
            if right == dest: return [["addl", left, dest]]
            return [
                ["movl", left, dest],
                ["addl", right, dest],
            ]
        elif isinstance(node, UnaryOp):
            if type(node.op) == USub:
                return [
                    ["movl", value(node.operand), dest],
                    ["negl", dest],
                ]
            elif type(node.op) == Not:
                return [
                    ["not", value(node.operand), dest]
                ]
        elif isinstance(node, Compare):
            op_map = {
                Eq: "eq",
                NotEq: "ne",
                Is: "is"
            }
            op = op_map.get(type(node.ops[0]))
            return [[op, value(node.left), value(node.comparators[0]), dest]]
        elif isinstance(node, Call):
            return [
                *call(node.func, node.args), 
                ["movl", "%eax", dest],
            ]
        elif isinstance(node, Subscript):
            return [["movl", value(node), dest]]
        elif isinstance(node, Dict):
            return [["movl", {value(k): value(v) for k, v in zip(node.keys, node.values)}, dest]]
        elif isinstance(node, List):
            return [["movl", [value(elt) for elt in node.elts], dest]]
        else:
            raise Exception(f"s_ir: unrecognized AST node {node}")
        
    # for each node in module add result to arr
    s_ir_arr = []
    for node in tree.body:
        if isinstance(node, Assign):
            s_ir_arr.extend(assign(node.value, value(node.targets[0])))
        elif isinstance(node, Expr):
            if isinstance(node.value, Call) and node.value.func.id != "int":
                s_ir_arr.extend(call(node.value.func, node.value.args))
        elif isinstance(node, If):
            s_ir_arr.extend(ifelse(node.test, node.body, node.orelse))
        elif isinstance(node, While):
            s_ir_arr.extend(while_loop(node.body))
        elif isinstance(node, Break):
            if while_depth == -1:
                raise Exception(f"s_ir: break not in while")
            s_ir_arr.append(["jmp", f"while_end{while_depth}"])
        else:
            raise Exception(f"s_ir: unrecognized AST node {node}")
    
    return s_ir_arr
