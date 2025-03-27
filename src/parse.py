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
        return Module(
            body=[arg for arg in args if arg is not None], 
            type_ignores=[]
        )
    
    def stmt(self, args):
        if isinstance(args[0], Assign):
            args[0].targets.ctx = Store()
        return args[0]
    
    def expr(self, args):
        return Expr(args[0])
    
    def obj(self, args):
        return args[0]
    
    def big(self, args):
        return args[0]
    
    def subscription(self, args):
        return Subscript(
            value=args[0],
            slice=args[1],
            ctx=Load()
        )
    
    def dictionary(self, args):
        if args[0]:
            keys, values = zip(*args[0])
            keys = list(keys)
            values = list(values)
        else:
            keys = values = []
        return Dict(
            keys=keys,
            values=values
        )
    
    def dict_datum(self, args):
        return [(args[0], args[1])]
    
    def dict_data(self, args):
        return [*args[0], (args[1], args[2])]
    
    def listionary(self, args):
        if not args[0]: args[0] = []
        return List(
            elts=[arg for arg in args[0] if arg is not None],
            ctx=Load()
        )
    
    def list_datum(self, args):
        return args
    
    def list_data(self, args):
        return [*args[0], args[1]]
            
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
    
    def comp_expr(self, args):
        return args[0]
    
    def not_expr(self, args):
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
    
    def comp_(self, args):
        return Compare(
            left=args[0], 
            ops=[args[1]], 
            comparators=[args[2]]
        )
    
    def not_(self, args):
        return UnaryOp(
            op=Not(), 
            operand=args[1]
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
    
    def int_(self, args):
        return Call(
            func = Name(id="int", ctx=Load()), 
            args = [args[1]],
            keywords = []
        )
    
    def true_(self, args):
        return Constant(value=True)
    
    def false_(self, args):
        return Constant(value=False)
    
    def eq_(self, args):
        return Eq()
    
    def ne_(self, args):
        return NotEq()
    
    def is_(self, args):
        return Is()
    
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
    
    def empty(self, args):
        return None
    
    def DECIMAL_INT(self, args):
        return Constant(value = int(args))
    
    def NAME(self, args):
        return Name(id = args.value, ctx = Load())
    
    def BREAK(self, args):
        return Break()