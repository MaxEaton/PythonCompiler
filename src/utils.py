#!/usr/bin/env python3.10

import os
import copy
import ast
from ast import *
import subprocess
import sys
import argparse

functions = [
    "print",
    "eval",
    "input"
]

from verify import *
from uniqify import *
from flatten import *
from generate_s import *
from generate_p0 import *
