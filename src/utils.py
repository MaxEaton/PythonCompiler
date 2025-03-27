#!/usr/bin/env python3.10

import os
import copy
import ast
import queue
from ast import *
import subprocess
import sys
import argparse
import logging
from lark import Lark, Tree, Transformer
from lark.indenter import Indenter

functions = [
    "print",
    "eval",
    "input",
    "int",
]

keywords = [
    "break",
]

# 0: the indices/reg of write set; removed if in read set
# 1: the indices/reg of read set 
# 2: the indices/reg of interference whitelist
# 3: the indices/reg of interference blacklist
# 4: the indices that cannot both be on stack
# 5: the index of writeback if applicable
s_ir_insts = {
    "cmpl": [[], [1,2], [], [], [1,2], []],
    "eq": [[3], [1,2], ["%eax",3], [], [1,2], [3]],
    "ne": [[3], [1,2], ["%eax",3], [], [1,2], [3]],
    "is": [[3], [1,2], ["%eax",3], [], [1,2], [3]],
    "je": [[], [], [], [], [], []],
    "jmp": [[], [], [], [], [], []],
    "movl": [[2], [1], [2], [1], [1,2], [2]],
    "negl": [[], [1], [1], [], [], [1]],
    "not": [[2], [1], [2,"%eax"], [], [], [2]],
    "addl": [[], [1,2], [2], [], [1,2], [2]],
    "xorl": [[], [1,2], [2], [], [1,2], [2]],
    "call": [["%eax"], [2], ["%eax", "%ecx", "%edx"], [], [], []],
}

t_desugar_cnt = 0
t_flatten_cnt = 0
t_explicate_cnt = 0
t_spill_cnt = 0
t_ir_cnt = 0
if_cnt = 0
while_cnt = 0
while_depth = -1
explicate_cnt = 0

from parse import *
from verify import *
from desugar import *
from flatten import *
from generate_p0 import *
from s_ir import *
from cfg import *
from explicate import *
from liveness import *
from interference import *
from coloring import *
from spillage import *
from generate_s import *
