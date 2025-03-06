#!/usr/bin/env python3.10

from utils import *

def interference(s_ir_arr, liveness_arr):
    '''
    Takes assembly ir and liveness sets and returns interference graph.

    :param s_ir_arr: list of assembly ir
    :param liveness_arr: liveness sets
    :return: dictionary representing a graph
    '''
    # initialize graph with pre-existing interferences between registers
    interference_graph = {
        "%eax": {"%ecx", "%edx", "%ebx", "%edi", "%esi"},
        "%ecx": {"%eax", "%edx", "%ebx", "%edi", "%esi"},
        "%edx": {"%eax", "%eax", "%ebx", "%edi", "%esi"},
        "%ebx": {"%eax", "%ecx", "%edx", "%edi", "%esi"},
        "%edi": {"%eax", "%ecx", "%edx", "%ebx", "%esi"},
        "%esi": {"%eax", "%ecx", "%edx", "%ebx", "%edi"},
    }
    for liveness_var in liveness_arr:
        for x in liveness_var:
            interference_graph[x] = set()
    
    for i in range(len(s_ir_arr)):
        if s_ir_arr[i][0] in ["movl"]:
            for live_var in liveness_arr[i+1]:
                if live_var != s_ir_arr[i][1] and live_var != s_ir_arr[i][2] and s_ir_arr[i][2] in interference_graph:
                    interference_graph[live_var].add(s_ir_arr[i][2])
                    interference_graph[s_ir_arr[i][2]].add(live_var)
        elif s_ir_arr[i][0] in ["addl"]:
            for live_var in liveness_arr[i+1]:
                if live_var != s_ir_arr[i][2] and s_ir_arr[i][2] in interference_graph:
                    interference_graph[live_var].add(s_ir_arr[i][2])
                    interference_graph[s_ir_arr[i][2]].add(live_var)
        elif s_ir_arr[i][0] in ["call"]:
            for live_var in liveness_arr[i+1]:
                for call_reg in ["%eax", "%ecx", "%edx"]:
                    interference_graph[live_var].add(call_reg)
                    interference_graph[call_reg].add(live_var)
    return interference_graph
