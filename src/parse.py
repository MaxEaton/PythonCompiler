#!/usr/bin/env python3.10

from utils import *

class ToAst(Transformer): 
    def module(self, args):
        return Module(body = args, type_ignores = [])
    
    def statement(self, args):
        if isinstance(args[0], Assign):
            args[0].targets.ctx = Store()
        else:
            args[0] = Expr(args[0])
        return args[0]
    
    def expression(self, args):
        return args[0]
    
    def add_expr(self, args):
        return args[0]
    
    def neg_expr(self, args):
        return args[0]
    
    def term(self, args):
        return args[0]
    
    def printer(self, args):
        return Expr(Call(func=Name(id="print", ctx=Load()), args=[args[0]], keywords=[]))
    
    def assign(self, args):
        args[0].ctx = Store()
        return Assign(targets = [args[0]], value = args[1])
    
    def add(self, args):
        return BinOp(left = args[0], op = Add(), right = args[1])
    
    def neg(self, args):
        return UnaryOp(op = USub(), operand = args[0])
    
    def evalinput(self, args):
        return Call(func = Name(id = "eval", ctx = Load()), args = [Call(func = Name(id = "input", ctx = Load()), args = [], keywords = [])], keywords = [])
    
    def NAME(self, args):
        return Name(id = args, ctx = Load())
    
    def DECIMAL_INT(self, args):
        return Constant(value = int(args))
    