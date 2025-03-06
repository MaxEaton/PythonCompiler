#!/usr/bin/env python3.10

from utils import *

def generate_s(s_ir_arr, color_dict):
    home_dict = {}
    max_val = 5
    regs = ["%eax", "%ecx", "%edx", "%ebx", "%edi", "%esi"]
    for key, value in color_dict.items():
        if value < 6:
            home_dict[key] = regs[value]
        else:
            if value > max_val: max_val = value
            home_dict[key] = f"-{(value-5)*4}(%ebp)"
    
    max_val -= 5

    # instructions every function starts with  
    prog_s = ( 
        ".globl main\n"
        "  main:\n"
        "  pushl %ebp\n"
        "  movl %esp, %ebp\n"
        "  subl ${buffer}, %esp\n"
        "  pushl %ebx\n"
        "  pushl %esi\n"
        "  pushl %edi\n"
    ).format(buffer=max_val*4)

    for line in s_ir_arr:
        if line[0] in ["movl", "addl"]:
            if (not isinstance(line[1], int) and line[1] not in home_dict) or (not isinstance(line[2], int) and line[2] not in home_dict): continue
            r1 = home_dict[line[1]] if not isinstance(line[1], int) else f"${line[1]}"
            r2 = home_dict[line[2]] if not isinstance(line[2], int) else f"${line[2]}"
            if line[0] in ["movl"] and r1 == r2: continue
            prog_s += f"  {line[0]} {r1}, {r2}\n"
        elif line[0] in ["negl"]:
            if (not isinstance(line[1], int) and line[1] not in home_dict): continue
            r1 = home_dict[line[1]] if not isinstance(line[1], int) else f"${line[1]}"
            prog_s += f"  {line[0]} {r1}\n"
        elif line[0] in ["call"]:
            if line[2] is not None:
                arg = home_dict[line[2]] if not isinstance(line[2], int) else f"${line[2]}"
                if arg != "%eax": prog_s += f"  movl {arg}, %eax\n"
            prog_s += f"  pushl %eax\n"
            prog_s += f"  {line[0]} {line[1]}\n"
            prog_s += f"  addl $4, %esp\n"
    
    # instructions every function ends with
    prog_s += ( 
        "  popl %edi\n"
        "  popl %esi\n"
        "  popl %ebx\n"
        "  movl $0, %eax\n"
        "  movl %ebp, %esp\n"
        "  popl %ebp\n"
        "  ret\n"
    )
    
    return prog_s
