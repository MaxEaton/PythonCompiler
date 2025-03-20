#!/usr/bin/env python3.10

from utils import *

def liveness(blocks):
    '''
    Computes the liveness information for a list of basic blocks. 
    
    :param blocks: list of Block objects representing the basic blocks in the program
    :return: the modified list of blocks with updated liveness information
    '''
    for i in range(len(blocks)): blocks[i].reset_liveness_arr()
    get_key = lambda line, x: line[x] if isinstance(x, int) else x
    
    # add each block from bottom to top to queue
    q = queue.Queue()
    for i in range(len(blocks)-1, -1, -1): q.put(blocks[i])
    
    while not q.empty():
        block = q.get()
        # perform liveness analysis on block
        for j in range(len(block.lines)-1, -1, -1):
            line = block.lines[j]
            curr = set(block.liveness_arr[j+1])
            s_ir_inst = s_ir_insts.get(line[0])
            if s_ir_inst:
                for w in s_ir_inst[0]:
                    curr.discard(get_key(line, w))
                for r in s_ir_inst[1]:
                    r = get_key(line, r)
                    if r: curr.add(r)
            block.liveness_arr[j] |= {item for item in curr if not isinstance(item, int)}
        # update dependent blocks and add them to queue if added anything new
        for dep in block.deps:
            prev = set(dep.liveness_arr[-1])
            dep.liveness_arr[-1] |= block.liveness_arr[0]
            if dep.liveness_arr[-1] != prev: q.put(dep)
    
    if blocks[0].liveness_arr[0]:
        raise Exception(f"liveness: uninitialize variables {blocks[0].liveness_arr[0]}")
        
    return blocks
