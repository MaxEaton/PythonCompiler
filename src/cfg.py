#!/usr/bin/env python3.10

from utils import *

class Block:
    '''
    Basic block in a program with its corresponding lines of code, dependencies, labels, and liveness sets. 

    :param lines: list of instructions in the block
    :param deps: dependencies associated with the block
    :param label: unique identifier for the block
    :param liveness_arr: liveness sets for the block
    '''
    def __init__(self, lines, deps, label):
        self.lines = lines
        self.deps = deps
        self.label = label
    def reset_liveness_arr(self):
        self.liveness_arr = [set() for _ in range(len(self.lines)+1)]
        
def cfg(s_ir_arr_dict):
    '''
    Constructs a Control Flow Graph from a given IR array.

    :param s_ir_arr_dict: dict of list of x86 IR instructions representing the program
    :return: list of Block objects representing the CFG
    '''
    blocks_dict = {}
    for func in s_ir_arr_dict.keys():
        blocks = []
        jmp = True
        label = func
        labels, lines = {}, []
        for line in s_ir_arr_dict[func][0]:
            if line[0] in ["movl", "addl", "negl", "cmpl", "eq", "ne", "is", "not", "call"]:
                # if not a jump instruction add to accumulator
                lines.append(line)
            elif line[0] in ["je", "jmp"]:
                # if jump instruction create new block and reset accumulator
                lines.append(line)
                blocks.append(Block(lines, [] if jmp else [blocks[-1]], label))
                labels[label] = blocks[-1]
                label, lines = None, []
                jmp = line[0] == "jmp"
            else:
                # if label create new block unless empty then record new label
                if len(lines):
                    blocks.append(Block(lines, [] if jmp else [blocks[-1]], label))
                    labels[label] = blocks[-1]
                    jmp = False
                label, lines = line[0], [line]

        blocks.append(Block(lines, [] if jmp else [blocks[-1]], label))
        labels[label] = blocks[-1]
        
        # for each jump, add dependence to corresponding label
        for block in blocks:
            for line in block.lines:
                if line[0] in ["je", "jmp"]:
                    labels[line[1]].deps.insert(0, block)

        blocks_dict[func] = (blocks, s_ir_arr_dict[func][1])
   
    return blocks_dict
