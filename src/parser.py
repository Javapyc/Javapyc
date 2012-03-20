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

class Expr(AST):
    pass

class BinaryExpr(Expr):
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

class Term(Expr):
    pass

class BinaryTerm(Expr):
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

class UnaryFactor(Term):
    def __init__(self, expr):
        AST.__init__(self, (expr,))
        self.expr = expr

class Negate(UnaryFactor):
    def value(self):
        return -self.expr.value()

class Not(UnaryFactor):
    pass

class Integer(Factor):
    def __init__(self, val):
        AST.__init__(self, tuple())
        self.val = val
    def __repr__(self):
        return "Integer('{0}')".format(self.val)
    def value(self):
        return int(self.val.val)

class ExprParser(GenericParser):
    def __init__(self, start='expr'):
        GenericParser.__init__(self, start)
    
    def p_expr_plus(self, args):
        r'expr ::= expr + term'
        return Plus(args[0], args[2])
    
    def p_expr_minus(self, args):
        r'expr ::= expr - term'
        return Minus(args[0], args[2])
    
    def p_expr_term(self, args):
        r'expr ::= term'
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
    
    def p_neg_factor(self, args):
        r'factor ::= - factor'
        return Negate(args[1])
    
    def p_not_factor(self, args):
        r'factor ::= ! factor'
        return Not(args[1])

    def p_factor_int(self, args):
        r'factor ::= Integer'
        return Integer(args[0])

    def p_factor_expr(self, args):
        r'factor ::= ( expr )'
        return args[1]

    def typestring(self, token):
        return token.typename()

def dump(node, indent=0):
    def iprint(node):
        print('  ' * indent, end='')
        print(str(node))
    iprint(node)
    for child in node.children:
        dump(child, indent+1)


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

            parser = ExprParser()
            tree = parser.parse(tokens)

            dump(tree)
            print("Value: ", tree.value())

if __name__ == '__main__':
    main()

