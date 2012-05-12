#!/usr/bin/python3

import lexer
from spark import *

from fileutils import InputFile
import argparse
import sys

import ast

class ProgramGrammar:
    def p_program_program(self, args):
        r'program ::= mainclass classlist'
        return ast.Program( args[0], args[1] )
    
    def p_classlist_empty(self, args):
        r'classlist ::= '
        return tuple()
    def p_classlist_class(self, args):
        r'classlist ::= classdecl'
        return tuple(args)
    def p_classlist_classes(self, args):
        r'classlist ::= classdecl classlist'
        return (args[0],) + args[1]

class MainClassDeclGrammar:
    def p_mainclass(self, args):
        r'mainclass ::= class ID { public static void main ( String [ ] ID ) { stmtlist } }'
        # args[1] is ID, args[11] is ID, args[14] is stmtlist
        return ast.MainClassDecl(args[1].val, args[11].val, args[14])

class ClassDeclGrammar:
    def p_classdecl_object(self,args):
        r'classdecl ::= class ID { classvarlist methoddecllist }'
        return ast.BaseClassDecl(args[1].val, None, args[3], args[4])
    
    def p_classdecl_extends(self,args):
        r'classdecl ::= class ID extends ID { classvarlist methoddecllist }'
        return ast.DerivedClassDecl(args[1].val, args[3].val, args[5], args[6])
    
    def p_classvarlist_empty(self, args):
        r'classvarlist ::= '
        return tuple()
    def p_classvarlist_var(self, args):
        r'classvarlist ::= classvar'
        return tuple(args)
    def p_classvarlist_vars(self, args):
        r'classvarlist ::= classvar classvarlist'
        return (args[0],) + args[1]

    def p_classvar(self, args):
        r'classvar ::= type ID ;'
        return ast.ClassVarDecl(args[0], args[1].val)
    
    def p_methoddecllist_empty(self, args):
        r'methoddecllist ::= '
        return tuple()
    def p_methoddecllist_methoddecl(self, args):
        r'methoddecllist ::= methoddecl'
        return tuple(args)
    def p_methoddecllist_methoddecls(self, args):
        r'methoddecllist ::= methoddecl methoddecllist'
        return (args[0],) + args[1]

class MethodDeclGrammar:
    def p_methoddecl_all(self, args):
        r'methoddecl ::= public type ID ( formallist ) { stmtlist return expr ; }'
        return ast.MethodDecl(args[1], args[2].val, args[4], args[7], args[9])

class FormalGrammar:
    def p_formal_typeID(self, args):
        r'formal ::= type ID'
        return ast.Formal(args[0], args[1].val)

    def p_formallist_empty(self, args):
        r'formallist ::= '
        return tuple()
    def p_formallist_formal(self, args):
        r'formallist ::= formal'
        return tuple(args)
    def p_formallist_formals(self, args):
        r'formallist ::= formal , formallist'
        return (args[0],) + args[2]

class TypeGrammar:
    def p_type_int(self, args):
        r'type ::= int'
        return ast.IntType
    def p_type_boolean(self, args):
        r'type ::= boolean'
        return ast.BoolType
    def p_type_string(self, args):
        r'type ::= String'
        return ast.StringType
    def p_type_object(self, args):
        r'type ::= ID'
        return ast.ObjectType(args[0].val)

class StmtGrammar:
    def p_stmt_call(self, args):
        r'stmt ::= methodcall ;'
        return ast.MethodCall(args[0])
    def p_stmt_stmtlist(self, args):
        r'stmt ::= { stmtlist }'
        return ast.StmtList(args[1])
    def p_stmt_decl_type(self, args):
        r'stmt ::= type ID = expr ;'
        return ast.Decl(args[0], args[1].val, args[3])
    def p_stmt_assignment(self, args):
        r'stmt ::= ID = expr ;'
        return ast.Assignment(args[0].val, args[2])
    def p_stmt_print(self, args):
        r'stmt ::= System.out.println ( expr ) ;'
        return ast.Print(args[2])
    def p_stmt_printf(self, args):
        r'stmt ::= System.out.printf ( formatstring ) ;'
        return ast.Printf(args[2])

    def p_stmt_if(self, args):
        r'stmt ::= if ( expr ) stmt'
        return ast.If(args[2], args[4])
    def p_stmt_ifelse(self, args):
        r'stmt ::= if ( expr ) withelse else stmt'
        return ast.IfElse(args[2], args[4], args[6])
    def p_stmt_while(self, args):
        r'stmt ::= while ( expr ) stmt'
        return ast.While(args[2], args[4])
    def p_stmt_break(self, args):
        r'stmt ::= break ;'
        return ast.Break()

    def p_withelse_ifwithelse(self, args):
        r'withelse ::= if ( expr ) withelse else withelse'
        return ast.IfElse(args[2], args[4], args[6])
    def p_withelse_call(self, args):
        r'withelse ::= methodcall ;'
        return ast.MethodCall(args[0])
    def p_withelse_stmtlist(self, args):
        r'withelse ::= { stmtlist }'
        return ast.StmtList(args[1])
    def p_withelse_decl_type(self, args):
        r'withelse ::= type ID = expr ;'
        return ast.Decl(args[0], args[1].val, args[3])
    def p_withelse_assignment(self, args):
        r'withelse ::= ID = expr ;'
        return ast.Assignment(args[0].val, args[2])
    def p_withelse_print(self, args):
        r'withelse ::= System.out.println ( expr ) ;'
        return ast.Print(args[2])
    def p_withelse_printf(self, args):
        r'withelse ::= System.out.printf ( formatstring ) ;'
        return ast.Printf(args[2])

    def p_withelse_while(self, args):
        r'withelse ::= while ( expr ) stmt'
        return ast.While(args[2], args[4])
    def p_withelse_break(self, args):
        r'withelse ::= break ;'
        return ast.Break()
    
    def p_stmtlist_empty(self, args):
        r'stmtlist ::= '
        return tuple()
    def p_stmtlist_stmt(self, args):
        r'stmtlist ::= stmt'
        return tuple(args)
    def p_stmtlist_stmts(self, args):
        r'stmtlist ::= stmt stmtlist'
        return (args[0],) + args[1]

class ExprGrammar:
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
        r'term ::= term * unaryfactor'
        return ast.Mult(args[0], args[2])
    def p_term_div(self, args):
        r'term ::= term / unaryfactor'
        return ast.Div(args[0], args[2])
    def p_term_factor(self, args):
        r'term ::= unaryfactor'
        return args[0]
    
    def p_unaryfactor_neg(self, args):
        r'unaryfactor ::= - unaryfactor'
        return ast.Negate(args[1])
    def p_unaryfactor_not(self, args):
        r'unaryfactor ::= ! unaryfactor'
        return ast.Not(args[1])
    def p_unaryfactor_factor(self, args):
        r'unaryfactor ::= factor'
        return args[0]

    def p_factor_string(self, args):
        r'factor ::= string'
        return ast.String(args[0])
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
    def p_factor_methodcall(self, args):
        r'factor ::= methodcall'
        return args[0]
    def p_factor_expr(self, args):
        r'factor ::= ( expr )'
        return args[1]
    def p_factor_pow(self, args):
        r'factor ::= Math.pow ( expr , expr )'
        return ast.Pow(args[2], args[4])
    def p_factor_stringformat(self, args):
        r'factor ::= String.format ( formatstring )'
        return ast.StringFormat(args[2])

    def p_methodcall_call(self, args):
        r'methodcall ::= factor . ID ( paramlist )'
        return ast.Call(args[0], args[2].val, args[4])
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
    
    def p_formatstring(self, args):
        r'formatstring ::= string formatstringarglist '
        return ast.FormatString(args[0], args[1])
    def p_string_single(self, args):
        r'string ::= StringLiteral'
        return args[0].val
    def p_string_list(self, args):
        r'string ::= StringLiteral string'
        return args[0].val + args[1]
    def p_formatstringarglist_empty(self, args):
        r'formatstringarglist ::= '
        return tuple()
    def p_formatstringarglist_args(self, args):
        r'formatstringarglist ::= , formatstringargs'
        return args[1]
    def p_formatstringargs_empty(self, args):
        r'formatstringargs ::= '
        return tuple()
    def p_formatstringargs_expr(self, args):
        r'formatstringargs ::= expr'
        return tuple(args)
    def p_formatstringargs_exprs(self, args):
        r'formatstringargs ::= expr , formatstringargs'
        return (args[0],) + args[2]

    def typestring(self, token):
        return token.typename()

class ProgramParser(ProgramGrammar, 
                    MainClassDeclGrammar, 
                    ClassDeclGrammar, 
                    MethodDeclGrammar, 
                    FormalGrammar, 
                    TypeGrammar, 
                    StmtGrammar, 
                    ExprGrammar, 
                    GenericParser):
    def __init__(self):
        GenericParser.__init__(self, 'program')

    def typestring(self, token):
        return token.typename()

class ExprParser(ExprGrammar, GenericParser):
    def __init__(self):
        GenericParser.__init__(self, 'expr')

def dump(node, fout):
    def dumpNode(node, indent):
        def iprint(node):
            for b in indent[:-1]:
                if b:
                    print('| ', end='', file=fout)
                else:
                    print('  ', end='', file=fout)
            if len(indent):
                print('+-', end='', file=fout)
            print(str(node), file=fout)

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

        parser = ExprParser()
        tree = parser.parse(tokens)

        dump(tree, sys.stdout)

if __name__ == '__main__':
    main()

