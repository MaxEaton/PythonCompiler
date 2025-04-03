#!/usr/bin/env python3.10

from utils import *

if __name__ == "__main__":
    path_py = sys.argv[1]
    if not path_py.endswith('.py'):
        raise Exception(f"compile: argument not a valid python file")
    
    prog_py = ""
    with open(path_py) as file: 
        for line in file.read().split('\n'):
            prog_py += line.split('#', 1)[0] + "\n"
    
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "grammar.lark"), 'r') as file_lark:
        prog_lark = file_lark.read()
    parser = Lark(prog_lark, parser="lalr", start="module", debug=True, transformer=ToAst(), postlex=PyIndenter())
    
    tree = parser.parse(prog_py)
    tree = uniquify(tree)
    
    tree = unify(tree)
    tree, main_heap = free_list(tree)
    tree = heapify(tree, set(), main_heap)
    tree = closurify(tree)

    tree = desugar(tree)
    tree = flatten(tree)

    prog_flat = generate_p0(tree, 0)
    path_flat = (path_py)[:-3] + ".flatpy"
    with open(path_flat, "w") as file_flat: file_flat.write(prog_flat)
    print(f"Wrote to: {path_flat}")

    s_ir_arr_dict = s_ir(tree)
    blocks_dict = cfg(s_ir_arr_dict)
    blocks_dict = explicate(blocks_dict)

    tmps_arr = []
    prev_set = {
        "%eax": 0,
        "%ecx": 1,
        "%edx": 2,
        "%ebx": 3,
        "%edi": 4,
        "%esi": 5,
    }

    while True:
        blocks_dict = liveness(blocks_dict)
        interference_graph = interference(blocks_dict)
        color_dict = coloring(dict(interference_graph), tmps_arr, prev_set)
        for key, value in color_dict.items():
            if value >= 6: prev_set[key] = value
        blocks_dict, tmps_arr_ = spillage(blocks_dict, color_dict)
        if not tmps_arr_: break
        tmps_arr.extend(tmps_arr_)
    
    prog_s = generate_s(blocks_dict, color_dict)
    path_s = (path_py)[:-3] + ".s"
    with open(path_s, "w") as file_s: file_s.write(prog_s)
    print(f"Wrote to: {path_s}")
    