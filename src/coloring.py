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
    color_dict = {node: None for node in interference_graph}
    saturation_graph = {node: set() for node in interference_graph}
    
    # remove all previously spilled variables from consideration
    for node, color in prev_set.items():
        color_dict[node] = color
        for n in interference_graph[node]: saturation_graph[n].add(color)
        del interference_graph[node]
    
    # prioritize by tmp -> max saturation degree -> max interference degree
    # set color to be the next available color then add to saturation and remove from consideration
    while interference_graph:
        curr_node = max(interference_graph, key=lambda k: (len(saturation_graph[k]), len(interference_graph[k])))
        if tmps_arr: curr_node = tmps_arr.pop()
        colors = {color_dict[n] for n in interference_graph[curr_node]}
        color_dict[curr_node] = next(i for i in range(len(colors) + 1) if i not in colors)
        for n in interference_graph[curr_node]: saturation_graph[n].add(curr_node)
        del interference_graph[curr_node]
 
    return color_dict
