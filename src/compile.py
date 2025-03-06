#!/usr/bin/env python3.10

from utils import *

if __name__ == "__main__":
    path_py = sys.argv[1]
    if not path_py.endswith('.py'):
        raise Exception(f"compile: argument not a valid python file")
    
    prog_py = ""
    with open(path_py) as file:
            prog_py = file.read()
    
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "grammar.lark"), 'r') as file_lark:
            grammar = file_lark.read()
        
    parser = Lark(grammar, parser="lalr", start="module", debug=True, transformer=ToAst())
    tree = parser.parse(prog_py)
    
    tree = verify(tree)
    tree = uniqify(tree)
    
    tree = flatten(tree)
    prog_p0 = generate_p0(tree)
    path_p0 = (path_py)[:-3] + ".flatpy"
    try:
        with open(path_p0, "w") as file_p0:
            file_p0.write(prog_p0)
            print(f"Wrote to: {path_p0}")
    except Exception as e:
        print("Error writing file:", e)        
    
    s_ir_arr = s_ir(tree)
    
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
        liveness_arr = liveness(s_ir_arr)
        interference_graph = interference(s_ir_arr, liveness_arr)
        color_dict = coloring(interference_graph, tmps_arr, prev_set)
        for key, value in color_dict.items():
            if value >= 6: prev_set[key] = value
        s_ir_arr, tmps_arr_ = spillage(s_ir_arr, color_dict, len(tmps_arr))
        if not tmps_arr_: break
        tmps_arr.extend(tmps_arr_)
        
    prog_s = generate_s(s_ir_arr, color_dict)
    path_s = (path_py)[:-3] + ".s"
    try:
        with open(path_s, "w") as file_s:
            file_s.write(prog_s)
            print(f"Wrote to: {path_s}")
    except Exception as e:
        print("Error writing file:", e)
    