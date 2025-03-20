#!/usr/bin/env python3.10

from utils import *

def deadstore(blocks):
    '''
    Performs dead store elimination for a list of basic blocks. 
    
    :param blocks: list of Block objects representing the basic blocks in the program
    :return: the list of blocks with dead stores removed
    :return: whether any lines were modified to signify convergence
    '''
    modified = False
    for block in blocks:
        for j, line in enumerate(block.lines):
            s_ir_inst = s_ir_insts.get(line[0])
            if s_ir_inst and s_ir_inst[5] and (line[s_ir_inst[5][0]] not in block.liveness_arr[j+1]):
                del block.lines[j]
                del block.liveness_arr[j+1]
                modified = True
    
    return blocks, modified
