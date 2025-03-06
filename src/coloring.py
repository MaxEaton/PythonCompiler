#!/usr/bin/env python3.10

from utils import *

def coloring(interference_graph, tmps_arr, prev_set):
    '''
    Takes interference graph, array of temp variables, and the previous set to account for spillage in order to color the interference graph.

    :param interference_graph: dictionary representing interference graph
    :param tmps_arr: list of temp variables
    :param prev_set: list of previously spilled variables
    :return: dictionary representing a colored graph
    '''
    color_dict = {x: None for x in interference_graph.keys()}
    saturation_graph = {x: set() for x in interference_graph.keys()}
    for x in prev_set.keys():
        color_dict[x] = prev_set[x]
        for y in interference_graph[x]:
            saturation_graph[y].add(x)
        del interference_graph[x]
    
    while interference_graph:
        curr_node = max(interference_graph.keys(), key = lambda k: (len(saturation_graph[k]), len(interference_graph[k])))
        if tmps_arr: curr_node = tmps_arr.pop()
        colors = {color_dict[x] for x in interference_graph[curr_node]}
        curr = interference_graph[curr_node]
        del interference_graph[curr_node]
        i = 0
        while True:
            if i not in colors:
                color_dict[curr_node] = i
                break
            i += 1
        for x in curr:
            saturation_graph[x].add(curr_node)
            
    return color_dict
