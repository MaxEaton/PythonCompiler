#!/usr/bin/env python3.10

from utils import *

def spillage(blocks_dict, color_dict):
    '''
    Creates new temps upon memory to memory operations. 

    :param blocks: list of Block objects representing the basic blocks in the program
    :param color_dict: mapping of variables to register assignment
    :return: updated blocks with spillage code
    :return: list of added temporary variables
    '''
    global t_spill_cnt
    tmps_arr_ = []
    for blocks, _ in blocks_dict.values():
        for i in range(len(blocks)):
            block = blocks[i]
            for j, line in enumerate(block.lines):
                s_ir_inst = s_ir_insts.get(line[0])
                if s_ir_inst and len(s_ir_inst[4]) == 2:
                    op1 = line[s_ir_inst[4][0]]
                    op2 = line[s_ir_inst[4][1]]
                    if op1 in color_dict and color_dict[op1] >= 6 and op2 in color_dict and color_dict[op2] >= 6:
                        block.lines.insert(j, ["movl", line[1], f"t_spill_{t_spill_cnt}"])
                        block.lines[j+1][1] = f"t_spill_{t_spill_cnt}"
                        tmps_arr_.append(f"t_spill_{t_spill_cnt}")
                        t_spill_cnt += 1
                        j += 1
    
    return blocks_dict, tmps_arr_
