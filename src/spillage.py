#!/usr/bin/env python3.10

from utils import *

def spillage(s_ir_arr, color_dict, tmpi):
    '''
    Takes s_ir, the color dictionary, and a temp counter.

    :param s_ir_arr: array of instructions in the s_ir
    :param color_dict: dictionary of each variable's coloring
    :param tmpi: counter for temp variable assignment
    :return: s_ir and array of temp variables
    '''
    tmps_arr_ = []
    for i, line in enumerate(s_ir_arr):
        if line[0] in ["addl", "movl"] and line[1] in color_dict and color_dict[line[1]] >= 6 and line[2] in color_dict and color_dict[line[2]] >= 6: #if both registers are going to be spilled to the stack
            s_ir_arr.insert(i, ["movl", line[1], f"ir_tmp{tmpi}"])
            s_ir_arr[i+1][1] = f"ir_tmp{tmpi}"
            tmps_arr_.append(f"ir_tmp{tmpi}")
            tmpi += 1
            i += 1
    
    return s_ir_arr, tmps_arr_
