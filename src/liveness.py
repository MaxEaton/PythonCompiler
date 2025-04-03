#!/usr/bin/env python3.10

from utils import *

def hashify(obj):
    if isinstance(obj, (int, bool, str)):
        return obj
    elif isinstance(obj, list):  
        return tuple(x for x in obj)
    elif isinstance(obj, tuple):  
        return (obj,) 
    elif isinstance(obj, dict):  
        return frozenset((k, v) for k, v in obj.items())

def liveness(blocks_dict):
    '''
    Computes the liveness information for a list of basic blocks. 
    
    :param blocks: list of Block objects representing the basic blocks in the program
    :return: the modified list of blocks with updated liveness information
    '''
    get_key = lambda line, x: line[x] if isinstance(x, int) else x
    for func, (blocks, _) in blocks_dict.items():
        for i in range(len(blocks)): 
            blocks[i].reset_liveness_arr()
    
        # add each block from bottom to top to queue
        q = queue.Queue()
        for i in range(len(blocks)-1, -1, -1): q.put(blocks[i])
        
        while not q.empty():
            block = q.get()
            # perform liveness analysis on block
            if func != "main": block.liveness_arr[-1].add("%eax")
            for j in range(len(block.lines)-1, -1, -1):
                line = block.lines[j]
                curr = set(block.liveness_arr[j+1])
                s_ir_inst = s_ir_insts.get(line[0])
                if s_ir_inst:
                    for w in s_ir_inst[0]:
                        w = get_key(line, w)
                        if isinstance(w, (int, bool, list, dict, tuple)):
                            if isinstance(r, (list, tuple)):
                                for r_ in r:
                                    if not isinstance(r, (int, bool, list, dict, tuple)):
                                        curr.discard(r_)
                            elif isinstance(r, (dict)):
                                for r1, r2 in r.items():
                                    if not isinstance(r1, (int, bool, list, dict, tuple)):
                                        curr.discard(r1)
                                    if not isinstance(r2, (int, bool, list, dict, tuple)):
                                        curr.discard(r2)
                        elif w:
                            curr.discard(w)
                    targets = range(len(line[2])) if line[0] == "call" else s_ir_inst[1]
                    for r in targets:
                        r = get_key(line[2], r) if line[0] == "call" else get_key(line, r)
                        if isinstance(r, (int, bool, list, dict, tuple)):
                            if isinstance(r, (list, tuple)):
                                for r_ in r:
                                    if not isinstance(r_, (int, bool, list, dict, tuple)):
                                        curr.add(r_)
                            elif isinstance(r, (dict)):
                                for r1, r2 in r.items():
                                    if not isinstance(r1, (int, bool, list, dict, tuple)):
                                        curr.add(r1)
                                    if not isinstance(r2, (int, bool, list, dict, tuple)):
                                        curr.add(r2)
                        elif r:
                            curr.add(r)
                    if line[0] == "call" and line[1] not in functions: curr.add(line[1])
                block.liveness_arr[j] |= curr
            # update dependent blocks and add them to queue if added anything new
            for dep in block.deps:
                prev = set(dep.liveness_arr[-1])
                dep.liveness_arr[-1] |= block.liveness_arr[0]
                if dep.liveness_arr[-1] != prev: q.put(dep)
        
        if blocks[0].liveness_arr[0]:
            for missing in blocks[0].liveness_arr[0]:
                if not missing.startswith("t_fun") and missing not in functions and missing != "free_vars" and not missing.startswith("arg_"):
                    raise Exception(f"liveness: uninitialize variables {missing} in {func}")
        
    return blocks_dict
