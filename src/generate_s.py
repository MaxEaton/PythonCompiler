#!/usr/bin/env python3.10

from utils import *

def generate_s(tree):
    '''
    Takes flattened AST and converts to x86 assembly.

    :param tree: root of AST
    :return: a string that represents the equivalent x86 representation of the AST
    '''
    def call(func, args):
        '''
        Takes function and args to converts to x86 assembly.

        :param func: function node
        :param args: list of arg nodes
        :return: a string that represents the equivalent x86 representation of the function call
        '''
        # get function id
        id = None
        if func.id == "print":
            id = "print_int_nl"
        elif func.id == "eval":
            id = "eval_input_int"
        elif func.id == "input":
            return ""
        else:
            raise Exception(f"generate_s.call: unrecognized function {func.id}")
        # push function argument then call and pop
        return (assign(args[0], "%eax") if len(args) else "") + (
            "  pushl %eax\n"
            "  call {func}\n"
            "  addl $4, %esp\n"
        ).format(func=id)
    
    def assign(node, dest):
        '''
        Takes node and destination name to convert to x86 assembly. 

        :param node: value node
        :param dest: destination name string
        :return: a string that represents the equivalent x86 representation of the assignment
        '''
        if isinstance(node, Constant):
            # move const to dest
            return (
                "  movl ${value}, {dest}\n"
            ).format(value=node.value, dest=dest)
        elif isinstance(node, Name):
            # move var to eax then to dest
            return (
                "  movl -{offset}(%ebp), %eax\n"
                "  movl %eax, {dest}\n"
            ).format(offset=names[node.id], dest=dest)
        elif isinstance(node, BinOp):
            # assign ecx and eax then add and assign dest
            return assign(node.left, "%ecx") + assign(node.right, "%eax") + (
                "  addl %eax, %ecx\n"
                "  movl %ecx, {dest}\n"
            ).format(dest=dest)
        elif isinstance(node, UnaryOp):
            # assign ecx then negate and assign to dest
            return assign(node.operand, "%ecx") + (
                "  negl %ecx\n"
                "  movl %ecx, {dest}\n"
            ).format(dest=dest)
        elif isinstance(node, Call):
            # call function then assign to dest
            return call(node.func, node.args) + (
                "  movl %eax, {dest}\n"
            ).format(dest=dest)
        else:
            raise Exception(f"generate_s: unrecognized AST node {node}")
    
    # ensure root of tree
    if not isinstance(tree, Module):
        raise Exception(f"generate_s: unrecognized AST node {node}")
    
    # get all names and associate with offset
    names = {
        name: 4*(i+1)
        for i, name in enumerate(
            x.id
            for node in tree.body
            if isinstance(node, Assign)
            for x in node.targets
        )
    }
    
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
    ).format(buffer=len(names)*4)

    # traverse each flattened line
    for node in tree.body:
        if isinstance(node, Assign):
            prog_s += assign(node.value, f"-{names[node.targets[0].id]}(%ebp)")
        elif isinstance(node, Expr):
            if isinstance(node.value, Call):
                prog_s += call(node.value.func, node.value.args)
        else:
            raise Exception(f"generate_s: unrecognized AST node {node}")
    
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