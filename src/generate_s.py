#!/usr/bin/env python3.10

from utils import *

def get_name(var, home_dict, str_list):
    if isinstance(var, int):
        return f"${var}"
    elif var in home_dict:
        return home_dict[var]
    else:
        str_list.add(var)
        return f"${var}"

def generate_s(blocks_dict, color_dict):
    '''
    Traverse X86 IR and convert to X86

    :param blocks: list of Block objects with X86 IR
    :param color_dict: mapping of variables to register assignment
    :return: a string that represents the equivalent X86 representation to the X86 IR
    '''
    prog_s = ""
    # store attr names
    str_list = set()
    for func, (blocks, args) in blocks_dict.items():
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
        prog_s += (
            ".globl {func}\n"
            "{func}:\n"
            "  pushl %ebp\n"
            "  movl %esp, %ebp\n"
            "  subl ${buffer}, %esp\n"
            "  pushl %ebx\n"
            "  pushl %esi\n"
            "  pushl %edi\n"
        ).format(func=func,buffer=max_val*4)

        for i, arg in enumerate(args):
            if arg in home_dict:
                prog_s += f"  movl {(i+2)*4}(%ebp), %eax\n"
                prog_s += f"  movl %eax, {home_dict[arg]}\n"

        for block in blocks:
            for line in block.lines:
                if line[0] in ["movl", "addl", "xorl", "cmpl"]:
                    if isinstance(line[1], tuple):
                        prog_s += f"  call get_subscript\n"
                    # optimize out if not assigned a home or is a register
                    if (not isinstance(line[1], int) and line[1] not in home_dict) or (not isinstance(line[2], int) and line[2] not in home_dict): continue
                    # get registers from homes or directly from line
                    r1 = get_name(line[1], home_dict, str_list)
                    r2 = get_name(line[2], home_dict, str_list)
                    # optimize out redundant moves
                    if line[0] in ["movl"] and r1 == r2: continue
                    prog_s += f"  {line[0]} {r1}, {r2}\n"
                elif line[0] in ["negl"]:
                    # optimize out if not assigned a home or is a register
                    if (not isinstance(line[1], int) and line[1] not in home_dict): continue
                    # get registers from homes or directly from line
                    r1 = get_name(line[1], home_dict, str_list)
                    prog_s += f"  {line[0]} {r1}\n"
                elif line[0] in ["call"]:
                    function = line[1] if line[1] in functions else f"*{home_dict[line[1]]}"
                    if function == "create_closure":
                        prog_s += f"  call .get_pc{line[2][0][-1]}\n"
                        prog_s += f"  .get_pc{line[2][0][-1]}:\n"
                        prog_s += f"  pop {home_dict[line[2][0]]}\n"
                        prog_s += f"  addl $({line[2][0]} - .get_pc{line[2][0][-1]}), {home_dict[line[2][0]]}\n"
                    for arg in reversed(line[2]):
                        arg = get_name(arg, home_dict, str_list)
                        prog_s += f"  pushl {arg}\n"
                    prog_s += f"  {line[0]} {function}\n"
                    prog_s += f"  addl ${4*len(line[2])}, %esp\n"
                elif line[0] in ["eq", "ne"]:
                    # optimize out if not assigned a home or is a register
                    if (not isinstance(line[1], int) and line[1] not in home_dict) or (not isinstance(line[2], int) and line[2] not in home_dict) or (not isinstance(line[3], int) and line[3] not in home_dict): continue
                    # get registers from homes or directly from line
                    r1 = get_name(line[1], home_dict, str_list)
                    r2 = get_name(line[2], home_dict, str_list)
                    r3 = get_name(line[3], home_dict, str_list)
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

        if func == "main": prog_s += "  movl $0, %eax\n"
        prog_s += (
            "  popl %edi\n"
            "  popl %esi\n"
            "  popl %ebx\n"
            "  movl %ebp, %esp\n"
            "  popl %ebp\n"
            "  ret\n"
        )
    
    data_section = ".section .data\n"
    for var in str_list:
        data_section += f"{var}:\n  .asciz \"{var}\"\n"
    data_section += ".section .text\n"
    prog_s = data_section + prog_s

    return prog_s
