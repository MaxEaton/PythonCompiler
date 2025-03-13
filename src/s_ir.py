#!/usr/bin/env python3.10

from utils import *

def s_ir(tree):
    '''
    Takes flattened AST and returns assembly ir.

    :param tree: root of AST
    :return: list of assembly ir
    '''
    global if_cnt, while_cnt, while_depth, t_cmpl_cnt
    
    def value(node):
        # return node value based on type
        if isinstance(node, Constant): return node.value
        elif isinstance(node, Name): return node.id
        raise Exception(f"s_ir: unrecognized AST node {node}")
    
    def call(func, args):
        # map function and add args
        name_map = {
            "print": "print_int_nl",
            "eval": "eval_input_int",
        }
        name = name_map.get(func.id)
        if not name:
            raise Exception(f"s_ir.call: unrecognized function {func.id}")
        arg = None if len(args) == 0 or name == "eval_input_int" else value(args[0])
        return ["call", name, arg]
    
    def cmpl(test1, test2):
        # handle different types of comparators
        global t_cmpl_cnt
        if isinstance(test1, Constant) and isinstance(test1, Constant):
            t_cmpl_cnt += 1
            return [
                ["movl", value(test2), f"t_comp_{t_cmpl_cnt-1}"], 
                ["cmpl", value(test1), f"t_comp_{t_cmpl_cnt-1}"]
            ]
        elif isinstance(test1, Constant):
            return [["cmpl", value(test1), value(test2)]]
        else:
            return [["cmpl", value(test2), value(test1)]]
    
    def ifelse(test, body, orelse):
        # perform test and sandwhich between jumps and labels
        global if_cnt
        cnt = if_cnt
        if_cnt += 1
        return [
            *cmpl(Constant(value=0), test),
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
            return [
                ["movl", value(node.operand), dest],
                ["negl", dest],
            ]
        elif isinstance(node, Call):
            # SPECIAL: needed since compare must be wrapped in int()
            if node.func.id == "int":
                arg = node.args[0]
                if isinstance(arg, Compare):
                    op_map = {
                        Eq: "eq",
                        NotEq: "ne"
                    }
                    op = op_map.get(type(arg.ops[0]))
                    ret = cmpl(arg.left, arg.comparators[0])
                    ret[-1].append(dest)
                    ret[-1][0] = op
                    return ret
                elif isinstance(arg, UnaryOp):
                    ret = cmpl(Constant(value=0), arg.operand)
                    ret[-1].append(dest)
                    ret[-1][0] = "eq"
                    return ret
                else:
                    raise Exception(f"s_ir: unrecognized AST node {arg}")
            return [
                call(node.func, node.args), 
                ["movl", "%eax", dest],
            ]
        else:
            raise Exception(f"s_ir: unrecognized AST node {node}")
        
    
    # for each node in module add result to arr
    s_ir_arr = []
    for node in tree.body:
        if isinstance(node, Assign):
            s_ir_arr.extend(assign(node.value, node.targets[0].id))
        elif isinstance(node, Expr):
            if isinstance(node.value, Call) and node.value.func.id != "int":
                s_ir_arr.append(call(node.value.func, node.value.args))
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
