#!/usr/bin/env python3.10

from utils import *

def name_of(node):
    '''
    Finds name of given function or variable

    :param node: an AST node
    :return: a node name or node value
    '''
    if isinstance(node, Name):
        return node.id
    return name_of(node.value)

def free_list(node, args=set()):
    '''
    Given a node finds all of the free variables within the scope

    :param node: an AST node
    :param args: a set of arguments, empty by default
    :return: set of free nodes
    :return: the free list heap
    '''
    if isinstance(node, Module):
        free_list.used = set() 
        free_list.bound = set(functions) | args
        for x in node.body: 
            if isinstance(x, FunctionDef):
                free_list(x)
        for x in node.body: 
            if not isinstance(x, FunctionDef): 
                free_list(x)
        # heap to track variables used in function definitions
        free_list.heap = set() 
        for x in node.body:
            if isinstance(x, FunctionDef):
                # heaped variables are the intersection of bound and free variables
                free_list.heap |= (free_list.bound & x.free) 
                # discard function name from used variables
                free_list.used.discard(x.name) 
        # free variables are those that are used but not bound
        free_list.free = free_list.used - free_list.bound 
        return node, free_list.heap
    elif isinstance(node, Assign):
        free_list(node.targets[0])
        free_list(node.value)
    elif isinstance(node, Expr):
        free_list(node.value)
    elif isinstance(node, (Constant, Break)):
        pass
    elif isinstance(node, Name):
        if isinstance(node.ctx, Load):
            free_list.used.add(node.id)
        else:
            free_list.bound.add(node.id)
    elif isinstance(node, BinOp):
        free_list(node.left)
        free_list(node.right)
    elif isinstance(node, UnaryOp):
        free_list(node.operand)
    elif isinstance(node, Call):
        free_list(node.func)
        for arg in node.args: free_list(arg)
    elif isinstance(node, BoolOp):
        for value in node.values: free_list(value)
    elif isinstance(node, IfExp):
        free_list(node.test)
        free_list(node.body)
        free_list(node.orelse)
    elif isinstance(node, Compare):
        free_list(node.left)
        for c in node.comparators: free_list(c)
    elif isinstance(node, (If, While)):
        free_list(node.test)
        for x in node.body: free_list(x)
        for x in node.orelse: free_list(x)
    elif isinstance(node, Subscript):
        free_list(node.value)
        free_list(node.slice)
    elif isinstance(node, Dict):
        for key in node.keys: free_list(key)
        for value in node.values: free_list(value)
    elif isinstance(node, List):
        for elt in node.elts: free_list(elt)
    elif isinstance(node, Return):
        free_list(node.value)
    elif isinstance(node, FunctionDef):
        free_list.bound.add(node.name)
        curr_used = free_list.used
        curr_bound = set(free_list.bound)
        free_list(Module(body=node.body), set([arg.arg for arg in node.args.args]))
        # remove arguments from free list
        for arg in node.args.args: free_list.free.discard(arg.arg) 
        node.free = free_list.free
        node.heap = free_list.heap
        free_list.used = curr_used
        # add free variables to used set
        free_list.used |= free_list.free 
        free_list.bound = curr_bound
    else:
        raise Exception(f"free_list: unrecognized AST node {node}")
