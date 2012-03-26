#!/usr/bin/python

import lexer
from spark import *

from fileutils import InputFile
import argparse
import sys

class AST:
    def __init__(self, children):
        self.children = children
    def classname(self):
        return self.__class__.__name__
    def __repr__(self):
        return "{0}".format(self.classname())


class Program(AST):
    def __init__(self, stmts):
        AST.__init__(self, stmts)

class Stmt(AST):
    pass
class Print(Stmt):
    def __init__(self, expr):
        AST.__init__(self, (expr,))

class Expr(AST):
    pass
class Or(Expr):
    def __init__(self, left, right):
        AST.__init__(self, (left,right))
    def value(self):
        left, right = self.children
        return left.value() or right.value()

class AndExpr(Expr):
    pass
class And(AndExpr):
    def __init__(self, left, right):
        AST.__init__(self, (left,right))
    def value(self):
        left, right = self.children
        return left.value() and right.value()

class EqualExpr(AndExpr):
    pass
class BinaryEqualExpr(EqualExpr):
    def __init__(self, left, right):
        AST.__init__(self, (left,right))
class Equal(BinaryEqualExpr):
    def value(self):
        left, right = self.children
        return left.value() == right.value()
class NotEqual(BinaryEqualExpr):
    def value(self):
        left, right = self.children
        return left.value() != right.value()

class CompExpr(EqualExpr):
    pass
class BinaryCompExpr(CompExpr):
    def __init__(self, left, right):
        AST.__init__(self, (left,right))
class LessThan(BinaryCompExpr):
    def value(self):
        left, right = self.children
        return left.value() < right.value()
class GreaterThan(BinaryCompExpr):
    def value(self):
        left, right = self.children
        return left.value() > right.value()
class LessThanEqualTo(BinaryCompExpr):
    def value(self):
        left, right = self.children
        return left.value() <= right.value()
class GreaterThanEqualTo(BinaryCompExpr):
    def value(self):
        left, right = self.children
        return left.value() >= right.value()

class AlgExpr(CompExpr):
    pass
class BinaryExpr(AlgExpr):
    def __init__(self, left, right):
        AST.__init__(self, (left,right))
        self.left = left
        self.right = right
class Plus(BinaryExpr):
    def value(self):
        return self.left.value() + self.right.value()
class Minus(BinaryExpr):
    def value(self):
        return self.left.value() - self.right.value()

class Term(AlgExpr):
    pass
class BinaryTerm(AlgExpr):
    def __init__(self, left, right):
        AST.__init__(self, (left,right))
        self.left = left
        self.right = right
class Mult(BinaryTerm):
    def value(self):
        return self.left.value() * self.right.value()
class Div(BinaryTerm):
    def value(self):
        return int(self.left.value() / self.right.value())

class Factor(Term):
    pass
class UnaryFactor(Factor):
    def __init__(self, expr):
        AST.__init__(self, (expr,))
        self.expr = expr
class Negate(UnaryFactor):
    def value(self):
        return -self.expr.value()
class Not(UnaryFactor):
    def value(self):
        return not self.expr.value()
class NewInstance(Factor):
    def __init__(self, name):
        AST.__init__(self, tuple())
        self.name = name
    def __repr__(self):
        return "New({0})".format(self.name)
    def value(self):
        return None
class Scalar(Factor):
    def __repr__(self):
        return "({0}){1}".format(self.typename(), self.val)
class Integer(Scalar):
    def __init__(self, val):
        AST.__init__(self, tuple())
        self.val = val.val
    def typename(self):
        return 'int'
    def value(self):
        return int(self.val)
class Boolean(Scalar):
    def __init__(self, val):
        AST.__init__(self, tuple())
        self.val = val
    def typename(self):
        return 'bool'
    def value(self):
        return self.val
class Null(Factor):
    def __init__(self):
        AST.__init__(self, tuple())
    def __repr__(self):
        return 'null'
    def value(self):
        return None
class This(Factor):
    def __init__(self):
        AST.__init__(self, tuple())
    def __repr__(self):
        return 'this'
    def value(self):
        return None
class ID(Factor):
    def __init__(self, name):
        AST.__init__(self, tuple())
        self.name = name
    def __repr__(self):
        return 'ID({0})'.format(self.name)
    def value(self):
        return None
class Call(Factor):
    def __init__(self, obj, func, args):
        AST.__init__(self, (obj,) + tuple(args))
        self.obj = obj
        self.func = func
    def __repr__(self):
        return 'Call({0})'.format(self.func)
    def value(self):
        return None

class StmtParser():
    def p_stmt_print(self, args):
        r'stmt ::= System.out.println ( expr ) ;'
        return Print(args[2])

class ExprParser():
    def p_expr_or(self, args):
        r'expr ::= expr || andexpr'
        return Or(args[0], args[2])
    def p_expr_andexpr(self, args):
        r'expr ::= andexpr'
        return args[0]

    def p_andexpr_and(self, args):
        r'andexpr ::= andexpr && equalexpr'
        return And(args[0], args[2])
    def p_andexpr_equalexpr(self, args):
        r'andexpr ::= equalexpr'
        return args[0]
    
    def p_equalexpr_equal(self, args):
        r'equalexpr ::= equalexpr == compexpr'
        return Equal(args[0], args[2])
    def p_equalexpr_notequal(self, args):
        r'equalexpr ::= equalexpr != compexpr'
        return NotEqual(args[0], args[2])
    def p_equalexpr_compexpr(self, args):
        r'equalexpr ::= compexpr'
        return args[0]
    
    def p_compexpr_lessthan(self, args):
        r'compexpr ::= compexpr < algexpr'
        return LessThan(args[0], args[2])
    def p_compexpr_greaterthan(self, args):
        r'compexpr ::= compexpr > algexpr'
        return GreaterThan(args[0], args[2])
    def p_compexpr_lessthanequalto(self, args):
        r'compexpr ::= compexpr <= algexpr'
        return LessThanEqualTo(args[0], args[2])
    def p_compexpr_greaterthanequalto(self, args):
        r'compexpr ::= compexpr >= algexpr'
        return GreaterThanEqualTo(args[0], args[2])
    def p_compexpr_algexpr(self, args):
        r'compexpr ::= algexpr'
        return args[0]
    
    def p_algexpr_plus(self, args):
        r'algexpr ::= algexpr + term'
        return Plus(args[0], args[2])
    def p_algexpr_minus(self, args):
        r'algexpr ::= algexpr - term'
        return Minus(args[0], args[2])
    def p_algexpr_term(self, args):
        r'algexpr ::= term'
        return args[0]
    
    def p_term_mult(self, args):
        r'term ::= term * factor'
        return Mult(args[0], args[2])
    def p_term_div(self, args):
        r'term ::= term / factor'
        return Div(args[0], args[2])
    def p_term_factor(self, args):
        r'term ::= factor'
        return args[0]
    
    def p_factor_neg(self, args):
        r'factor ::= - factor'
        return Negate(args[1])
    def p_factor_not(self, args):
        r'factor ::= ! factor'
        return Not(args[1])
    def p_factor_int(self, args):
        r'factor ::= Integer'
        return Integer(args[0])
    def p_factor_true(self, args):
        r'factor ::= true'
        return Boolean(True)
    def p_factor_false(self, args):
        r'factor ::= false'
        return Boolean(False)
    def p_factor_null(self, args):
        r'factor ::= null'
        return Null()
    def p_factor_this(self, args):
        r'factor ::= this'
        return This()
    def p_factor_new(self, args):
        r'factor ::= new ID ( )'
        return NewInstance(args[1].val)
    def p_factor_id(self, args):
        r'factor ::= ID'
        return ID(args[0].val)
    def p_factor_call(self, args):
        r'factor ::= expr . ID ( paramlist )'
        return Call(args[0], args[2].val, args[4])
    def p_factor_expr(self, args):
        r'factor ::= ( expr )'
        return args[1]

    def p_paramlist_empty(self, args):
        r'paramlist ::= '
        return tuple()
    def p_paramlist_param(self, args):
        r'paramlist ::= param'
        return tuple(args)
    def p_paramlist_params(self, args):
        r'paramlist ::= param , paramlist'
        return (args[0],) + args[2]
    def p_param_expr(self, args):
        r'param ::= expr'
        return args[0]

    def typestring(self, token):
        return token.typename()

class ProgramParser(ExprParser, StmtParser, GenericParser):
    def __init__(self):
        GenericParser.__init__(self, 'program')
    
    def p_program_stmtlist(self, args):
        r'program ::= stmtlist'
        return args[0]

    def p_stmtlist_empty(self, args):
        r'stmtlist ::= '
        return tuple()
    def p_stmtlist_stmt(self, args):
        r'stmtlist ::= stmt'
        return tuple(args)
    def p_stmtlist_stmts(self, args):
        r'stmtlist ::= stmt stmtlist'
        return (args[0],) + args[1]
    
    def typestring(self, token):
        return token.typename()

class SingleExprParser(ExprParser, GenericParser):
    def __init__(self):
        GenericParser.__init__(self, 'expr')

def dump(node):
    def dumpNode(node, indent):
        def iprint(node):
            for b in indent[:-1]:
                if b:
                    print('| ', end='')
                else:
                    print('  ', end='')
            if len(indent):
                print('+-', end='')
            print(str(node))

        iprint(node)

        if len(indent):
            indent[-1] -= 1
        indent.append(len(node.children))

        for child in node.children:
            dumpNode(child, indent)
        indent.pop()
    dumpNode(node, [])


def main():
    parser = argparse.ArgumentParser(description='parse some MiniJava')
    parser.add_argument('files', nargs='+', type=InputFile)
    args = parser.parse_args()
    if not args:
        return

    for inputFile in args.files:
        with inputFile as f:
            s = f.read()
            scanner = lexer.ExpressionScanner()
            tokens = scanner.tokenize(s)

            parser = SingleExprParser()
            tree = parser.parse(tokens)

            dump(tree)
            print("Value: ", tree.value())

if __name__ == '__main__':
    main()

