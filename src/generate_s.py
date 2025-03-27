#!/usr/bin/env python3.10

from utils import *

def generate_s(blocks, color_dict):
    '''
    Traverse X86 IR and convert to X86

    :param blocks: list of Block objects with X86 IR
    :param color_dict: mapping of variables to register assignment
    :return: a string that represents the equivalent X86 representation to the X86 IR
    '''
    # assign homes based on provided colors
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
    
    # set buffer on stack
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

    for block in blocks:
        for line in block.lines:
            if line[0] in ["movl", "addl", "xorl", "cmpl"]:
                # optimize out if not assigned a home or is a register
                if isinstance(line[1], tuple):
                    prog_s += f"  call get_subscript\n"
                if (not isinstance(line[1], int) and line[1] not in home_dict) or (not isinstance(line[2], int) and line[2] not in home_dict): continue
                # get registers from homes or directly from line
                r1 = home_dict[line[1]] if not isinstance(line[1], int) else f"${line[1]}"
                r2 = home_dict[line[2]] if not isinstance(line[2], int) else f"${line[2]}"
                # optimize out redundant moves
                if line[0] in ["movl"] and r1 == r2: continue
                prog_s += f"  {line[0]} {r1}, {r2}\n"
            elif line[0] in ["negl"]:
                # optimize out if not assigned a home or is a register
                if (not isinstance(line[1], int) and line[1] not in home_dict): continue
                # get registers from homes or directly from line
                r1 = home_dict[line[1]] if not isinstance(line[1], int) else f"${line[1]}"
                prog_s += f"  {line[0]} {r1}\n"
            elif line[0] in ["call"]:
                for arg in reversed(line[2]):
                    arg = home_dict[arg] if not isinstance(arg, (int, bool, list, dict)) else f"${arg}"
                    prog_s += f"  pushl {arg}\n"
                prog_s += f"  {line[0]} {line[1]}\n"
                prog_s += f"  addl ${4*len(line[2])}, %esp\n"
            elif line[0] in ["eq", "ne"]:
                # optimize out if not assigned a home or is a register
                if (not isinstance(line[1], int) and line[1] not in home_dict) or (not isinstance(line[2], int) and line[2] not in home_dict) or (not isinstance(line[3], int) and line[3] not in home_dict): continue
                # get registers from homes or directly from line
                r1 = home_dict[line[1]] if not isinstance(line[1], int) else f"${line[1]}"
                r2 = home_dict[line[2]] if not isinstance(line[2], int) else f"${line[2]}"
                r3 = home_dict[line[3]] if not isinstance(line[3], int) else f"${line[3]}"
                if r2[0] == "$": prog_s += f"  cmpl {r2}, {r1}\n"
                else: prog_s += f"  cmpl {r1}, {r2}\n"
                # sete or setne for eq vs ne
                if line[0] in ["eq"]: prog_s += f"  sete %al\n"
                else: prog_s += f"  setne %al\n"
                # different instuction if r3 on stack
                if "%ebp" in r3: prog_s += f"  movb %al, {r3}\n"
                else: prog_s += f"  movzbl %al, {r3}\n"
            elif line[0] in ["je", "jmp"]:
                # jumps
                prog_s += f"  {line[0]} {line[1]}\n"
            else:
                # labels
                prog_s += f"{line[0]}:\n"
                
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
