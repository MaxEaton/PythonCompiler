#!/usr/bin/env python3.10

from utils import *

def liveness(s_ir_arr):
    '''
    Takes assembly ir and returns liveness sets.

    :param s_ir_arr: list of assembly ir
    :return: list of liveness sets
    '''
    liveness_arr = [set()]
    
    for line in reversed(s_ir_arr):
        curr = set(liveness_arr[-1])
        if line[0] in ["addl"]:
            curr.add(line[1])
            curr.add(line[2])
        elif line[0] in ["negl"]:
            curr.add(line[1])
        elif line[0] in ["movl"]:
            curr.discard(line[2])
            curr.add(line[1])
        elif line[0] in ["call"]:
            curr.discard("%eax")
            if line[2]:
                curr.add(line[2])
        liveness_arr.append({item for item in curr if not isinstance(item, int)})
    
    if liveness_arr[-1]:
        raise Exception(f"liveness: uninitialize variables {liveness_arr[-1]}")
    return list(reversed(liveness_arr))
