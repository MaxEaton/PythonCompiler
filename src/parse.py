#!/usr/bin/env python3.10

from utils import *

class PyIndenter(Indenter):
    '''
    Custom indenter for Python code to handle blocks
    '''
    NL_type = 'NEWLINE'
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    tab_len = 4

class ToAst(Transformer): 
    def module(self, args):
        return Module(body=[arg for arg in args if arg is not None], type_ignores=[])
    
    def stmt(self, args):
        if isinstance(args[0], Assign):
            args[0].targets.ctx = Store()
        return args[0]
    
    def expr(self, args):
        return Expr(args[0])
    
    def ternary(self, args):
        return args[0]
    
    def ternary_(self, args):
        return IfExp(
            test=args[2],
            body=args[0],
            orelse=args[4]
        )
    
    def or_expr(self, args):
        return args[0]
    
    def and_expr(self, args):
        return args[0]
    
    def add_expr(self, args):
        return args[0]
    
    def neg_expr(self, args):
        return args[0]
    
    def term(self, args):
        return args[0]
    
    def print_(self, args):
        return Expr(Call(
            func=Name(id="print", ctx=Load()), 
            args=[args[0]], 
            keywords=[])
        )
    
    def assign_(self, args):
        args[0].ctx = Store()
        return Assign(targets = [args[0]], value = args[1])
    
    def newline_(self, args):
        return None
    
    def or_(self, args):
        return BoolOp(
            values=[args[0], args[2]],
            op=Or()
        )
    
    def and_(self, args):
        return BoolOp(
            values=[args[0], args[2]],
            op=And()
        )
    
    def add_(self, args):
        return BinOp(left = args[0], op = Add(), right = args[1])
    
    def neg_(self, args):
        return UnaryOp(op = USub(), operand = args[0])
    
    def evalinput_(self, args):
        return Call(
            func = Name(id="eval", ctx=Load()), 
            args = [Call(func=Name(id="input", ctx=Load()), args=[], keywords=[])], 
            keywords = []
        )
    
    def not_(self, args):
        return Call(
            func = Name(id="int", ctx=Load()), 
            args = [UnaryOp(op=Not(), operand=args[2])],
            keywords = []
        )
    
    def comp_(self, args):
        return Call(
            func = Name(id="int", ctx=Load()), 
            args = [Compare(left=args[1], ops=[args[2]], comparators=[args[3]])],
            keywords = []
        )
    
    def eq(self, args):
        return Eq()
    
    def ne(self, args):
        return NotEq()
    
    def suite(self, args):
        return args
    
    def if_block(self, args):
        return If(
            test=args[1], 
            body=args[3], 
            orelse=[] if (len(args)<7 or not args[6]) else args[6]
        )
    
    def while_block(self, args):
        return While(
            test=args[1], 
            body=args[3], 
            orelse=[] if (len(args)<7 or not args[6]) else args[6]
        )
    
    def DECIMAL_INT(self, args):
        return Constant(value = int(args))
    
    def NAME(self, args):
        return Name(id = args.value, ctx = Load())
    
    def BREAK(self, args):
        return Break()
