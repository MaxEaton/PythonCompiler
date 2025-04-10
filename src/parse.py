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
            
    def lmd(self, args):
        return args[0]
            
    def lmd_(self, args):
        return Lambda(
            args=arguments(
                posonlyargs=[],
                args=args[1] if args[1] else [],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[]
            ), 
            body=args[2]
        )
            
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
    
    def assign_(self, args):
        args[0].ctx = Store()
        return Assign(targets = [args[0]], value = args[1])
    
    def return_(self, args):
        return Return(value=args[1])
    
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
    
    def func_(self, args):
        return Call(
            func = args[0], 
            args = [] if not args[1] else args[1], 
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
        return [arg for arg in args if arg is not None]
    
    def big(self, args):
        return args[0]
    
    def attribute(self, args):
        return Attribute(
            value=args[0],
            attr=args[1].id,
            ctx=Load()
        )

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
    
    def arg_(self, args):
        return [arg(args[0].id)]
    
    def args_data(self, args):
        return [*args[0], arg(args[1].id)]
    
    def inherit_data(self, inherits):
        if not isinstance(inherits[0], list): inherits[0] = [inherits[0]]
        return [*inherits[0], inherits[1]]

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
    
    def func_block(self, args):
        return FunctionDef(
            name=args[1].id,
            args=arguments(
                posonlyargs=[],
                args=args[2] if args[2] else [],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[]
            ), 
            body=args[4]
        )

    def class_block(self, args):
        return ClassDef(
            name=args[1].id,
            bases=[],
            body=args[3],
        )

    def class_in_block(self, args):
        if not isinstance(args[2], list): args[2] = [args[2]]
        return ClassDef(
            name=args[1].id,
            bases=args[2] if args[2][0] else [],
            body=args[4],
        )
    
    def empty(self, args):
        return None
    
    def DECIMAL_INT(self, args):
        return Constant(value = int(args))
    
    def NAME(self, args):
        return Name(id = args.value, ctx = Load())
    
    def PASS(self, args):
        return Pass()
    
    def BREAK(self, args):
        return Break()
