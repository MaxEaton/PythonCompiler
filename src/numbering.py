#!/usr/bin/env python3.10

from utils import *

def add(s, t, var=False):
    '''
    Given source and terminal, add to the numbering dictionary. 
    
    :param s: name of source
    :param t: name of terminal
    :param var: whether the terminal is a variable
    :return: the mapping of the source
    '''
    global number, number_dict
    if s not in number_dict:
        if isinstance(t, int):
            number_dict[s] = t
        else:
            number_dict[s] = f"{number}"
            if f"{number}" not in number_dict and var:
                number_dict[f"{number}"] = s
            number += 1
    return number_dict[s]
        
def numbering(blocks):
    '''
    Performs live value numbering for a list of basic blocks. 
    
    :param blocks: list of Block objects representing the basic blocks in the program
    :return: the list of blocks with copy folded and constant folded lines
    '''
    global number, number_dict, t_number_cnt
    for block in blocks:
        number_dict = {}
        number = 0
        force = False
        reassign = []
        for j, line in enumerate(block.lines):
            # add dependencies, source, and terminal for each instruction
            if line[0] in ["movl"]:
                op = line[1]
                index = 2
            elif line[0] in ["addl"]:
                add(line[1], line[1], True)
                add(line[2], line[2], True)
                if isinstance(number_dict[line[1]], int) and isinstance(number_dict[line[2]], int):
                    number_dict[line[2]] = number_dict[line[1]] + number_dict[line[2]]
                    block.lines[j] = ["movl", number_dict[line[2]], line[2]]
                    continue
                op = frozenset({line[0], number_dict[line[1]], number_dict[line[2]]})
                index = 2
            elif line[0] in ["negl"]:
                add(line[1], line[1], True)
                if isinstance(number_dict[line[1]], int):
                    number_dict[line[1]] = -number_dict[line[1]]
                    continue
                op = (line[0], number_dict[line[1]])
                index = 1
            elif line[0] in ["eq", "ne"]:
                add(line[1], line[1], True)
                add(line[2], line[2], True)
                if isinstance(number_dict[line[1]], int) and isinstance(number_dict[line[2]], int):
                    if line[0] in ["eq"]: number_dict[line[3]] = int(number_dict[line[1]] == number_dict[line[2]])
                    else: number_dict[line[3]] = int(number_dict[line[1]] != number_dict[line[2]])
                    continue
                op = frozenset({line[0], number_dict[line[1]], number_dict[line[2]]})
                index = 3
            else:
                # perform constant folding for all but cmpl
                if line[0] != "cmpl":
                    for k in range(1, len(line)):
                        if line[k] in number_dict and isinstance(number_dict[line[k]], int):
                            block.lines[j][k] = number_dict[line[k]]
                if line[0] == "call":
                    number_dict.pop("%eax", None)
                    add("%eax", "%eax")
                continue
            
            if line[index] not in number_dict or force:
                num = add(op, op, line[0]=="movl")
                force = line[0] == "movl"
                number_dict[line[index]] = number_dict[op]
                if isinstance(num, str) and num not in number_dict:
                    number_dict[num] = line[index]
                elif isinstance(num, str):
                    block.lines[j] = ["movl", number_dict[num], line[index]]
            else:
                # perform copy folding for all 
                swap = line[index]
                number_dict[f"t_number_{t_number_cnt}"] = number_dict[swap]
                block.lines.insert(j, ["movl", swap, f"t_number_{t_number_cnt}"])
                reassign.append(["movl", f"t_number_{t_number_cnt}", swap])
                for i in range(j+1, len(block.lines)):
                    for k in range(len(block.lines[i])):
                        if block.lines[i][k] == swap: 
                            block.lines[i][k] = f"t_number_{t_number_cnt}"
                t_number_cnt += 1
                force = True
                
        if block.lines and block.lines[-1][0] in ["je", "jmp"]:
            block.lines = block.lines[:-1] + reassign + block.lines[-1:]
        else:
            block.lines.extend(reassign)
            
    return blocks
