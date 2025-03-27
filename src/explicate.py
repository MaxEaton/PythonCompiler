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
        ["call", "is_int", [register]], #check if int
        ["cmpl", 1, "%eax"], #check if int
        ["je", f"if_int{explicate_cnt-1}"], #jump if int
        ["call", "is_bool", [register]], #check if bool
        ["cmpl", 1, "%eax"], #check if bool
        ["je", f"if_bool{explicate_cnt-1}"], #jump if bool
        ["call", "is_big", [register]], #check if big
        ["cmpl", 1, "%eax"], #check if big
        ["je", f"if_big{explicate_cnt-1}"], #jump if big
        [f"if_int{explicate_cnt-1}"], #if int
        ["call", "project_int", [register]],
        i1,
        ["call", "inject_int", ["%eax"]],
        ["jmp", f"explicate_end{explicate_cnt-1}"], #jump to end
        [f"if_bool{explicate_cnt-1}"], #if bool
        ["call", "project_bool", [register]],
        i2,
        ["call", "inject_int", ["%eax"]],
        ["jmp", f"explicate_end{explicate_cnt-1}"], #jump to end
        [f"if_big{explicate_cnt-1}"], #if big
        ["call", "project_big", [register]],
        i3,
        ["call", "inject_big", ["%eax"]],
        ["jmp", f"explicate_end{explicate_cnt-1}"], #jump to end
        [f"explicate_end{explicate_cnt-1}"] #end
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
        ["call", "is_int", [source]], #check if int
        ["cmpl", 1, "%eax"], #check if int
        ["je", f"if_int{explicate_cnt-1}"], #jump if int
        ["call", "is_bool", [source]], #check if bool
        ["cmpl", 1, "%eax"], #check if bool
        ["je", f"if_bool{explicate_cnt-1}"], #jump if bool
        ["call", "is_big", [source]], #check if big
        ["cmpl", 1, "%eax"], #check if big
        ["je", f"if_big{explicate_cnt-1}"], #jump if big
        [f"if_int{explicate_cnt-1}"], #if int
        ["call", "project_int", [source]],
        ["jmp", f"explicate_end{explicate_cnt-1}"], #jump to end
        [f"if_bool{explicate_cnt-1}"], #if bool
        ["call", "project_bool", [source]],
        ["jmp", f"explicate_end{explicate_cnt-1}"], #jump to end
        [f"if_big{explicate_cnt-1}"], #if big
        ["call", "project_big", [source]],
        ["jmp", f"explicate_end{explicate_cnt-1}"], #jump to end
        [f"explicate_end{explicate_cnt-1}"], #end
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

def explicate(blocks):
    '''
    Transforms X86 IR into an explicated form.
    
    :param blocks: list of Block objects representing the basic blocks in the program
    :return: list of Block objects with explication
    '''
    global t_explicate_cnt, explicate_cnt
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
                # set constant if can evaluate
                if isinstance(r1, (int, bool)) and isinstance(r2, (int, bool)): # TODO: move to numbering
                    if line[0] == "eq": block.lines[j] = ["movl", r1 == r2, line[3]]
                    else: block.lines[j] = ["movl", r1 != r2, line[3]]
                    continue
                # box r1 if needed
                if isinstance(r1, (int, bool)):
                    r1_new = f"t_explicate_{t_explicate_cnt}"
                    t_explicate_cnt += 1
                    box_block = box(r1)
                    block.lines[j:j] = box_block
                    j += len(box_block)
                    block.lines.insert(j, ["movl", "%eax", r1_new])
                    j += 1
                    r1 = r1_new
                # box r2 if needed
                if isinstance(r2, (int, bool)):
                    r2_new = f"t_explicate_{t_explicate_cnt}"
                    t_explicate_cnt += 1
                    box_block = box(r2)
                    block.lines[j:j] = box_block
                    j += len(box_block)
                    block.lines.insert(j, ["movl", "%eax", r2_new])
                    j += 1
                    r2 = r2_new
                # compare based on unboxed values
                cmpl_block = cmpl_box(r1, r2, line[0])
                block.lines[j:j] = cmpl_block
                j += len(cmpl_block)
                block.lines[j] = ["movl", "%eax", line[3]]
            elif line[0] == "is":
                r1 = line[1]
                r2 = line[2]
                # set constant if can evaluate
                if isinstance(r1, (int, bool)) and isinstance(r2, (int, bool)): # TODO: move to numbering
                    block.lines[j] = ["movl", r1 == r2 and type(r1) == type(r2), line[3]]
                    continue
                # box r1 if needed
                if isinstance(r1, (int, bool)):
                    box_block = box(r1)
                    block.lines[j:j] = box_block
                    j += len(box_block)
                    r1 = "%eax"
                # box r2 if needed
                if isinstance(r2, (int, bool)):
                    box_block = box(r2)
                    block.lines[j:j] = box_block
                    j += len(box_block)
                    r2 = "%eax"
                # compare boxed values
                block.lines[j] = ["eq", r1, r2, line[3]]
                block.lines.insert(j+1, ["call", "inject_bool", [line[3]]])
                j += 1
                block.lines.insert(j+1, ["movl", "%eax", line[3]])
                j += 1
            elif line[0] == "not":
                r1 = line[1]
                # set constant if can evaluate
                if isinstance(r1, (int, bool)): # TODO: move to numbering
                    block.lines[j] = ["movl", not r1, line[2]]
                    continue
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
            j += 1
    return blocks
