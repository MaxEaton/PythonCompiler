#!/usr/bin/env python3.10

from utils import *

def do_op(i1, i2, i3, register):
    '''
    Returns boilerplate for doing an operation.
    
    :param i1: instruction for int
    :param i2: instruction for bool
    :param i3: instruction for big
    :return: list of operation X86 explication
    '''
    global explicate_cnt
    explicate_cnt += 1
    return [
        ["call", "is_int", [register]],
        ["cmpl", 1, "%eax"],
        ["je", f"if_int{explicate_cnt-1}"],
        ["call", "is_bool", [register]],
        ["cmpl", 1, "%eax"],
        ["je", f"if_bool{explicate_cnt-1}"],
        ["call", "is_big", [register]],
        ["cmpl", 1, "%eax"],
        ["je", f"if_big{explicate_cnt-1}"],
        [f"if_int{explicate_cnt-1}"],
        ["call", "project_int", [register]],
        i1,
        ["call", "inject_int", ["%eax"]],
        ["jmp", f"explicate_end{explicate_cnt-1}"],
        [f"if_bool{explicate_cnt-1}"],
        ["call", "project_bool", [register]],
        i2,
        ["call", "inject_int", ["%eax"]],
        ["jmp", f"explicate_end{explicate_cnt-1}"],
        [f"if_big{explicate_cnt-1}"],
        ["call", "project_big", [register]],
        i3,
        ["call", "inject_big", ["%eax"]],
        ["jmp", f"explicate_end{explicate_cnt-1}"],
        [f"explicate_end{explicate_cnt-1}"]
    ]

def unbox(source, dest):
    '''
    Returns boilerplate for unbox.
    
    :param source: value to unbox
    :param dest: dest of unboxed
    :return: list of unbox X86 explication
    '''
    global explicate_cnt
    explicate_cnt += 1
    return [
        ["call", "is_int", [source]],
        ["cmpl", 1, "%eax"],
        ["je", f"if_int{explicate_cnt-1}"],
        ["call", "is_bool", [source]],
        ["cmpl", 1, "%eax"],
        ["je", f"if_bool{explicate_cnt-1}"],
        ["call", "is_big", [source]],
        ["cmpl", 1, "%eax"],
        ["je", f"if_big{explicate_cnt-1}"],
        [f"if_int{explicate_cnt-1}"],
        ["call", "project_int", [source]],
        ["jmp", f"explicate_end{explicate_cnt-1}"],
        [f"if_bool{explicate_cnt-1}"],
        ["call", "project_bool", [source]],
        ["jmp", f"explicate_end{explicate_cnt-1}"],
        [f"if_big{explicate_cnt-1}"],
        ["call", "project_big", [source]],
        ["jmp", f"explicate_end{explicate_cnt-1}"],
        [f"explicate_end{explicate_cnt-1}"],
        ["movl", "%eax", dest]
    ]

def box(source):
    '''
    Returns boilerplate for box.
    
    :param source: value to box
    :return: list of box X86 explication
    '''
    global t_explicate_cnt
    if isinstance(source, bool):
        return [["call", "inject_bool", [int(source)]]]
    elif isinstance(source, int):
        return [["call", "inject_int", [source]]]
    elif isinstance(source, list):
        pyobj_tmp = f"t_explicate_{t_explicate_cnt}"
        t_explicate_cnt += 1
        ret = [
            ["call", "inject_int", [len(source)]],
            ["call", "create_list", ["%eax"]],
            ["call", "inject_big", ["%eax"]],
            ["movl", "%eax", pyobj_tmp]
        ]
        for i in range(len(source)):
            val_tmp = f"t_explicate_{t_explicate_cnt}"
            t_explicate_cnt += 1
            ret.extend(box(source[i]))
            ret.append(["movl", "%eax", val_tmp])
            ret.append(["call", "inject_int", [i]])
            ret.append(["call", "set_subscript", [pyobj_tmp, "%eax", val_tmp]])
        ret.append(["movl", pyobj_tmp, "%eax"])
        return ret
    elif isinstance(source, dict):
        pyobj_tmp = f"t_explicate_{t_explicate_cnt}"
        t_explicate_cnt += 1
        ret = [
            ["call", "inject_int", [len(source)]],
            ["call", "create_dict", ["%eax"]],
            ["call", "inject_big", ["%eax"]],
            ["movl", "%eax", pyobj_tmp]
        ]
        for key, value in source.items():
            val_tmp = f"t_explicate_{t_explicate_cnt}"
            t_explicate_cnt += 1
            ret.extend(box(value))
            ret.append(["movl", "%eax", val_tmp])
            ret.extend(box(key))
            ret.append(["call", "set_subscript", [pyobj_tmp, "%eax", val_tmp]])
        ret.append(["movl", pyobj_tmp, "%eax"])
        return ret
    elif isinstance(source, tuple):
        if isinstance(source[1], tuple):
            return [
                ["call", "get_attr", [source[0], source[1][0]]]
            ]
        return [
            *box(source[1]),
            ["call", "get_subscript", [source[0], "%eax"]]
        ]
    else:
        return [["movl", source, "%eax"]]

def cmpl_box(r1, r2, eq):
    '''
    Returns boilerplate for cmpl.
    
    :param r1: name of first comparator
    :param r2: name of second comparator
    :param eq: whether eq or ne
    :return: list of cmpl X86 explication
    '''
    global explicate_cnt, t_explicate_cnt
    curr_cnt = explicate_cnt
    explicate_cnt += 1
    r1_proj = f"t_explicate_{t_explicate_cnt}"
    t_explicate_cnt += 1
    r2_proj = f"t_explicate_{t_explicate_cnt}"
    t_explicate_cnt += 1
    return [
        ["call", "is_big", [r1]],
        ["cmpl", 1, "%eax"],
        ["je", f"r1_big{curr_cnt}"],
        ["call", "is_int", [r1]],
        ["cmpl", 0, "%eax"],
        ["je", f"r1_bool{curr_cnt}"],
        [f"r1_int{curr_cnt}"],
        ["call", "project_int", [r1]],
        ["movl", "%eax", r1_proj],
        ["jmp", f"r1_small{curr_cnt}"],
        [f"r1_bool{curr_cnt}"],
        ["call", "project_bool", [r1]],
        ["movl", "%eax", r1_proj],
        ["jmp", f"r1_small{curr_cnt}"],

        [f"r1_big{curr_cnt}"],
        ["call", "is_big", [r2]],
        ["cmpl", 1, "%eax"],
        ["je", f"cmpl_big{curr_cnt}"],
        ["jmp", f"cmpl_zero{curr_cnt}"],

        [f"r1_small{curr_cnt}"],
        ["call", "is_big", [r2]],
        ["cmpl", 1, "%eax"],
        ["je", f"cmpl_zero{curr_cnt}"],
        ["call", "is_int", [r2]],
        ["cmpl", 0, "%eax"],
        ["je", f"r2_bool{curr_cnt}"],
        [f"r2_int{curr_cnt}"],
        ["call", "project_int", [r2]],
        ["movl", "%eax", r2_proj],
        ["jmp", f"cmpl_small{curr_cnt}"],
        [f"r2_bool{curr_cnt}"],
        ["call", "project_bool", [r2]],
        ["movl", "%eax", r2_proj],
        ["jmp", f"cmpl_small{curr_cnt}"],

        [f"cmpl_big{curr_cnt}"],
        ["call", "project_big", [r1]],
        ["movl", "%eax", r1_proj],
        ["call", "project_big", [r2]],
        ["movl", "%eax", r2_proj],
        ["call", "equal" if eq == "eq" else "not_equal", [r1_proj, r2_proj]],
        ["jmp", f"cmpl_end{curr_cnt}"],
        
        [f"cmpl_small{curr_cnt}"],
        [eq, r1_proj, r2_proj, "%eax"],
        ["jmp", f"cmpl_end{curr_cnt}"],

        [f"cmpl_zero{curr_cnt}"],
        ["movl", int(eq != "eq"), "%eax"],

        [f"cmpl_end{curr_cnt}"],
        ["call", "inject_bool", ["%eax"]]
    ]

def call_box(func, args):
    global explicate_cnt, t_explicate_cnt
    if func in functions: return [["call", func, args]]
    curr_cnt = explicate_cnt
    explicate_cnt += 1
    fun_ptr = f"t_explicate_{t_explicate_cnt}"
    t_explicate_cnt += 1
    free_vars = f"t_explicate_{t_explicate_cnt}"
    t_explicate_cnt += 1
    bounder = f"t_explicate_{t_explicate_cnt}"
    t_explicate_cnt += 1
    return [
        ["call", "is_big", [func]],
        ["cmpl", 1, "%eax"],
        ["je", f"func_big{curr_cnt}"],

        # built in functions like print
        ["call", func, args],
        ["jmp", f"call_end{curr_cnt}"],

        # switch between class, function bound, or unbound
        [f"func_big{curr_cnt}"],
        ["call", "is_class", [func]],
        ["cmpl", 1, "%eax"],
        ["je", f"func_class{curr_cnt}"],
        ["call", "is_function", [func]],
        ["cmpl", 1, "%eax"],
        ["je", f"func_function{curr_cnt}"],
        ["call", "is_bound_method", [func]],
        ["cmpl", 1, "%eax"],
        ["je", f"func_bound{curr_cnt}"],
        ["call", "is_unbound_method", [func]],
        ["cmpl", 1, "%eax"],
        ["je", f"func_unbound{curr_cnt}"],

        # unbound
        [f"func_unbound{curr_cnt}"],
        ["call", "get_function", [func]],
        ["movl", "%eax", func],
        ["call", "inject_big", [func]],
        ["movl", "%eax", func],
        ["call", "get_fun_ptr", [func]],
        ["movl", "%eax", fun_ptr],
        ["call", "get_free_vars", [func]],
        ["movl", "%eax", free_vars],
        ["call", fun_ptr, [free_vars, *args]],
        ["jmp", f"call_end{curr_cnt}"],

        # bound
        [f"func_bound{curr_cnt}"],
        ["call", "get_receiver", [func]],
        ["movl", "%eax", bounder],
        ["call", "inject_big", [bounder]],
        ["movl", "%eax", bounder],
        ["call", "get_function", [func]],
        ["movl", "%eax", func],
        ["call", "inject_big", [func]],
        ["movl", "%eax", func],
        ["call", "get_fun_ptr", [func]],
        ["movl", "%eax", fun_ptr],
        ["call", "get_free_vars", [func]],
        ["movl", "%eax", free_vars],
        ["call", fun_ptr, [free_vars, bounder, *args]],
        ["jmp", f"call_end{curr_cnt}"],

        # function
        [f"func_function{curr_cnt}"],
        ["call", "get_fun_ptr", [func]],
        ["movl", "%eax", fun_ptr],
        ["call", "get_free_vars", [func]],
        ["movl", "%eax", free_vars],
        ["call", fun_ptr, [free_vars, *args]],
        ["jmp", f"call_end{curr_cnt}"],

        # class
        [f"func_class{curr_cnt}"],
        ["call", "create_object", [func]],
        ["call", "inject_big", ["%eax"]],

        [f"call_end{curr_cnt}"],
    ]

def explicate(blocks_dict):
    '''
    Transforms X86 IR into an explicated form.
    
    :param blocks: list of Block objects representing the basic blocks in the program
    :return: list of Block objects with explication
    '''
    global t_explicate_cnt, explicate_cnt
    for blocks, _ in blocks_dict.values():
        for block in blocks:
            j = 0
            while j < len(block.lines):
                line = block.lines[j]
                if line[0] == "movl":
                    # box if constant, big, or subscript
                    if isinstance(line[1], (int, bool, list, dict, tuple)):
                        box_block = box(line[1])
                        block.lines[j:j] = box_block
                        j += len(box_block)
                        block.lines[j][1] = "%eax"
                        line[1] = "%eax"
                    # call for set subscript
                    if isinstance(line[2], tuple):
                        if isinstance(line[2][1], tuple):
                            block.lines[j] = ["call", "set_attr", [line[2][0], line[2][1][0], line[1]]]
                        else:
                            r1 = f"t_explicate_{t_explicate_cnt}"
                            t_explicate_cnt += 1
                            block.lines.insert(j, ["movl", line[1], r1])
                            j += 1
                            box_block = box(line[2][1])
                            block.lines[j:j] = box_block
                            j += len(box_block)
                            block.lines[j] = ["call", "set_subscript", [line[2][0], "%eax", r1]]
                elif line[0] == "addl":
                    r1 = line[1]
                    # unbox if variable
                    if isinstance(r1, (int, bool)): r1 = int(r1)
                    elif not isinstance(r1, (int, bool)):
                        r1 = f"t_explicate_{t_explicate_cnt}"
                        t_explicate_cnt += 1
                        unbox_block = unbox(line[1], r1)
                        block.lines[j:j] = unbox_block
                        j += len(unbox_block)
                    # perform add based on type
                    box_block = do_op(["addl", r1, "%eax"], ["addl", r1, "%eax"], ["call", "add", ["%eax", r1]], line[2])
                    block.lines[j:j] = box_block
                    j += len(box_block)
                    block.lines[j] = ["movl", "%eax", line[2]]
                elif line[0] == "negl":
                    # perform neg is int
                    box_block = do_op(["negl", "%eax"], ["negl", "%eax"], ["negl", "%eax"], line[1])
                    block.lines[j:j] = box_block
                    j += len(box_block)
                    block.lines[j] = ["movl", "%eax", line[1]]
                elif line[0] in ["eq", "ne"]:
                    r1 = line[1]
                    r2 = line[2]
                    cmpl_block = cmpl_box(r1, r2, line[0])
                    block.lines[j:j] = cmpl_block
                    j += len(cmpl_block)
                    block.lines[j] = ["movl", "%eax", line[3]]
                elif line[0] == "is":
                    r1 = line[1]
                    r2 = line[2]
                    block.lines[j] = ["eq", r1, r2, line[3]]
                    block.lines.insert(j+1, ["call", "inject_bool", [line[3]]])
                    j += 1
                    block.lines.insert(j+1, ["movl", "%eax", line[3]])
                    j += 1
                elif line[0] == "not":
                    r1 = line[1]
                    block.lines.insert(j, ["call", "is_true", [r1]])
                    j += 1
                    block.lines.insert(j, ["xorl", 1, "%eax"])
                    j += 1
                    block.lines.insert(j, ["call", "inject_bool", ["%eax"]])
                    j += 1
                    block.lines[j] = ["movl","%eax", line[2]]
                elif line[0] == "call":
                    for i in range(len(line[2])):
                        # box constants
                        if isinstance(line[2][i], bool):
                            arg = f"t_explicate_{t_explicate_cnt}"
                            t_explicate_cnt += 1
                            block.lines.insert(j, ["call", "inject_bool", [int(line[2][i])]])
                            j += 1
                            block.lines.insert(j, ["movl", "%eax", arg])
                            j += 1
                            block.lines[j][2][i] = arg
                        elif isinstance(line[2][i], int):
                            arg = f"t_explicate_{t_explicate_cnt}"
                            t_explicate_cnt += 1
                            block.lines.insert(j, ["call", "inject_int", [line[2][i]]])
                            j += 1
                            block.lines.insert(j, ["movl", "%eax", arg])
                            j += 1
                            block.lines[j][2][i] = arg
                    call_block = call_box(line[1], line[2])
                    block.lines[j:j] = call_block
                    j += len(call_block)
                    block.lines[j] = ["movl", "%eax", "%eax"]

                j += 1
    return blocks_dict
