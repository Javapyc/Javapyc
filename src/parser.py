#!/usr/bin/python3

import lexer
from spark import *

from fileutils import InputFile
import argparse
import sys

import ast

class StmtParser():
    def p_stmt_stmtlist(self, args):
        r'stmt ::= { stmtlist }'
        return ast.StmtList(args[1])
    def p_stmt_decl_int(self, args):
        r'stmt ::= int ID = expr ;'
        return ast.IntDecl(args[1], args[3])
    def p_stmt_decl_bool(self, args):
        r'stmt ::= boolean ID = expr ;'
        return ast.BoolDecl(args[1], args[3])
    def p_stmt_decl_type(self, args):
        r'stmt ::= ID ID = expr ;'
        return ast.TypeDecl(args[0], args[1], args[3])
    def p_stmt_assignment(self, args):
        r'stmt ::= ID = expr ;'
        return ast.Assignment(args[0], args[2])
    def p_stmt_print(self, args):
        r'stmt ::= System.out.println ( expr ) ;'
        return ast.Print(args[2])
    def p_stmt_if(self, args):
        r'stmt ::= if ( expr ) stmt else stmt'
        return ast.If(args[2], args[4], args[6])
    def p_stmt_while(self, args):
        r'stmt ::= while ( expr ) stmt'
        return ast.While(args[2], args[4])

    def p_stmtlist_empty(self, args):
        r'stmtlist ::= '
        return tuple()
    def p_stmtlist_stmt(self, args):
        r'stmtlist ::= stmt'
        return tuple(args)
    def p_stmtlist_stmts(self, args):
        r'stmtlist ::= stmt stmtlist'
        return (args[0],) + args[1]



class ExprParser():
    def p_expr_or(self, args):
        r'expr ::= expr || andexpr'
        return ast.Or(args[0], args[2])
    def p_expr_andexpr(self, args):
        r'expr ::= andexpr'
        return args[0]

    def p_andexpr_and(self, args):
        r'andexpr ::= andexpr && equalexpr'
        return ast.And(args[0], args[2])
    def p_andexpr_equalexpr(self, args):
        r'andexpr ::= equalexpr'
        return args[0]
    
    def p_equalexpr_equal(self, args):
        r'equalexpr ::= equalexpr == compexpr'
        return ast.Equal(args[0], args[2])
    def p_equalexpr_notequal(self, args):
        r'equalexpr ::= equalexpr != compexpr'
        return ast.NotEqual(args[0], args[2])
    def p_equalexpr_compexpr(self, args):
        r'equalexpr ::= compexpr'
        return args[0]
    
    def p_compexpr_lessthan(self, args):
        r'compexpr ::= compexpr < algexpr'
        return ast.LessThan(args[0], args[2])
    def p_compexpr_greaterthan(self, args):
        r'compexpr ::= compexpr > algexpr'
        return ast.GreaterThan(args[0], args[2])
    def p_compexpr_lessthanequalto(self, args):
        r'compexpr ::= compexpr <= algexpr'
        return ast.LessThanEqualTo(args[0], args[2])
    def p_compexpr_greaterthanequalto(self, args):
        r'compexpr ::= compexpr >= algexpr'
        return ast.GreaterThanEqualTo(args[0], args[2])
    def p_compexpr_algexpr(self, args):
        r'compexpr ::= algexpr'
        return args[0]
    
    def p_algexpr_plus(self, args):
        r'algexpr ::= algexpr + term'
        return ast.Plus(args[0], args[2])
    def p_algexpr_minus(self, args):
        r'algexpr ::= algexpr - term'
        return ast.Minus(args[0], args[2])
    def p_algexpr_term(self, args):
        r'algexpr ::= term'
        return args[0]
    
    def p_term_mult(self, args):
        r'term ::= term * factor'
        return ast.Mult(args[0], args[2])
    def p_term_div(self, args):
        r'term ::= term / factor'
        return ast.Div(args[0], args[2])
    def p_term_factor(self, args):
        r'term ::= factor'
        return args[0]
    
    def p_factor_neg(self, args):
        r'factor ::= - factor'
        return ast.Negate(args[1])
    def p_factor_not(self, args):
        r'factor ::= ! factor'
        return ast.Not(args[1])
    def p_factor_int(self, args):
        r'factor ::= Integer'
        return ast.Integer(args[0].val)
    def p_factor_true(self, args):
        r'factor ::= true'
        return ast.Boolean(True)
    def p_factor_false(self, args):
        r'factor ::= false'
        return ast.Boolean(False)
    def p_factor_null(self, args):
        r'factor ::= null'
        return ast.Null()
    def p_factor_this(self, args):
        r'factor ::= this'
        return ast.This()
    def p_factor_new(self, args):
        r'factor ::= new ID ( )'
        return ast.NewInstance(args[1].val)
    def p_factor_id(self, args):
        r'factor ::= ID'
        return ast.ID(args[0].val)
    def p_factor_call(self, args):
        r'factor ::= expr . ID ( paramlist )'
        return ast.Call(args[0], args[2].val, args[4])
    def p_factor_expr(self, args):
        r'factor ::= ( expr )'
        return args[1]
    def p_factor_pow(self, args):
        r'factor ::= Math.pow ( expr , expr )'
        return ast.Pow(args[2], args[4])

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
        return ast.Program(args[0])

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

class BasicParser(GenericParser):
    def __init__(self):
        GenericParser.__init__(self, 'program')
    
    def p_program_idlist(self, args):
        r'program ::= idlist'
        return ast.Program(args)
    def p_program_integerlist(self,args):
        r'program ::= integerlist'
        return ast.Program(args)
    
    def p_idlist_lists(self, args):
        r'idlist ::= ID idlist'
        return ast.IDList(ast.ID(args[0].val), args[1])
    def p_idlist_id(self,args):
        r'idlist ::= ID'
        return ast.ID(args[0].val)
    
    def p_integerlist_lists(self,args):
        r'integerlist ::= Integer integerlist'
        return ast.IntegerList(ast.Integer(args[0].val), args[1])
    def p_integerlist_integer(self,args):
        r'integerlist ::= Integer'
        return ast.Integer(args[0].val)

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
    parser.add_argument('inputFile', nargs='?', type=InputFile)
    args = parser.parse_args()
    if not args:
        return

    inputFile = args.inputFile
    if not inputFile:
        inputFile = sys.stdin

    import lexer

    with inputFile as f:
        s = f.read()
        scanner = lexer.MiniJavaScanner()
        tokens = scanner.tokenize(s)

        parser = BasicParser()
        tree = parser.parse(tokens)

        dump(tree)

if __name__ == '__main__':
    main()

