#!/usr/bin/env python3.10

from utils import *

def interference(blocks_dict):
    '''
    Constructs an interference graph based on the liveness information in the given basic blocks.

    :param blocks: list of Block objects representing the basic blocks in the program
    :return: a dictionary representing the interference graph, where each key is a variable and the value is a set of interfering variables
    '''
    get_key = lambda line, x: line[x] if isinstance(x, int) else x

    # initialize inherent interference between registers
    interference_graph = {
        "%eax": {"%ecx", "%edx", "%ebx", "%edi", "%esi"},
        "%ecx": {"%eax", "%edx", "%ebx", "%edi", "%esi"},
        "%edx": {"%eax", "%ecx", "%ebx", "%edi", "%esi"},
        "%ebx": {"%eax", "%ecx", "%edx", "%edi", "%esi"},
        "%edi": {"%eax", "%ecx", "%edx", "%ebx", "%esi"},
        "%esi": {"%eax", "%ecx", "%edx", "%ebx", "%edi"},
        "free_vars": set()
    }

    for blocks, args in blocks_dict.values():
        # initialize all variables to graph with empty set
        for block in blocks:
            for liveness_var in block.liveness_arr:
                for l in liveness_var:
                    if l not in interference_graph: interference_graph[l] = set()

        # add two way interference between arguments
        for i in args:
            for j in args:
                if i != j: interference_graph[i].add(j)
        for i in args:
            for j in ["%eax", "%ecx", "%edx", "%ebx", "%edi", "%esi"]:
                interference_graph[i].add(j)
                interference_graph[j].add(i)
        print(interference_graph)

        # add two way interference if in whitelist but not in blacklist 
        for block in blocks:
            for i, line in enumerate(block.lines):
                s_ir_inst = s_ir_insts.get(line[0])
                if not s_ir_inst: continue
                whitelist = {get_key(line, w) for w in s_ir_inst[2] if get_key(line, w) in interference_graph}
                blacklist = {get_key(line, b) for b in s_ir_inst[3] if get_key(line, b) in interference_graph}
                for live_var in block.liveness_arr[i+1]:
                    if live_var in blacklist: continue
                    for w in whitelist:
                        if w != live_var:
                            interference_graph[live_var].add(w)
                            interference_graph[w].add(live_var)
        
    return interference_graph
