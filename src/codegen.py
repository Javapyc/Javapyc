#!/usr/bin/python3

from code import CodeGen, CmpOp
import ast
import typechecker

import imp
import marshal
import time
import struct

from fileutils import InputFile
import argparse
import sys

def codegens(cls):
    '''
    Annotates a function that will be added to the given class
    that can generate code for itself
    '''
    def wrap(func):
        setattr(cls, 'codegen', func)
        return func
    return wrap

@codegens(ast.Program)
def codegen(self, c):
    mainclass, *classes = self.children
    mainclass.codegen(c)

@codegens(ast.MainClassDecl)
def codegen(self, c):
    stmts = self.children
    for stmt in stmts:
        stmt.codegen(c)

@codegens(ast.Decl)
def codegen(self, c):
    #TODO handle bool and custom types
    (expr,) = self.children
    expr.codegen(c)
    c.STORE_FAST(self.name)

@codegens(ast.Assignment)
def codegen(self, c):
    (expr,) = self.children
    expr.codegen(c)
    c.STORE_FAST(self.name)

@codegens(ast.Print)
def codegen(self, c):
    (expr,) = self.children
    c.LOAD_NAME('print')
    expr.codegen(c)
    c.CALL_FUNCTION(1)
    c.POP_TOP()

@codegens(ast.Printf)
def codegen(self, c):
    args = self.children
    c.LOAD_NAME('print')
    c.LOAD_CONST(self.string)
    for arg in args:
        arg.codegen(c)
    c.BUILD_TUPLE(len(args))
    c.BINARY_MODULO()
    c.CALL_FUNCTION(1)
    c.POP_TOP()

@codegens(ast.Or)
def codegen(self, c):
    left, right = self.children
    left.codegen(c)
    right.codegen(c)
    c.BINARY_OR()

@codegens(ast.And)
def codegen(self, c):
    left, right = self.children
    left.codegen(c)
    right.codegen(c)
    c.BINARY_AND()

@codegens(ast.Equal)
def codegen(self, c):
    left, right = self.children
    left.codegen(c)
    right.codegen(c)
    c.COMPARE_OP(CmpOp.EQUAL)

@codegens(ast.NotEqual)
def codegen(self, c):
    left, right = self.children
    left.codegen(c)
    right.codegen(c)
    c.COMPARE_OP(CmpOp.NOT_EQUAL)

@codegens(ast.LessThan)
def codegen(self, c):
    left, right = self.children
    left.codegen(c)
    right.codegen(c)
    c.COMPARE_OP(CmpOp.LESS_THAN)

@codegens(ast.GreaterThan)
def codegen(self, c):
    left, right = self.children
    left.codegen(c)
    right.codegen(c)
    c.COMPARE_OP(CmpOp.GREATER_THAN)

@codegens(ast.LessThanEqualTo)
def codegen(self, c):
    left, right = self.children
    left.codegen(c)
    right.codegen(c)
    c.COMPARE_OP(CmpOp.LESS_THAN_EQUAL_TO)

@codegens(ast.GreaterThanEqualTo)
def codegen(self, c):
    left, right = self.children
    left.codegen(c)
    right.codegen(c)
    c.COMPARE_OP(CmpOp.GREATER_THAN_EQUAL_TO)

@codegens(ast.Plus)
def codegen(self, c):
    self.left.codegen(c)
    self.right.codegen(c)
    c.BINARY_ADD()

@codegens(ast.Minus)
def codegen(self, c):
    self.left.codegen(c)
    self.right.codegen(c)
    c.BINARY_SUBTRACT()

@codegens(ast.Mult)
def codegen(self, c):
    self.left.codegen(c)
    self.right.codegen(c)
    c.BINARY_MULTIPLY()

@codegens(ast.Div)
def codegen(self, c):
    self.left.codegen(c)
    self.right.codegen(c)
    c.BINARY_FLOOR_DIVIDE()

@codegens(ast.Pow)
def codegen(self, c):
    a, b = self.children
    a.codegen(c)
    b.codegen(c)
    c.BINARY_POWER()

@codegens(ast.Negate)
def codegen(self, c):
    (expr,) = self.children
    expr.codegen(c)
    c.UNARY_INVERT()

@codegens(ast.Not)
def codegen(self, c):
    (expr,) = self.children
    expr.codegen(c)
    c.UNARY_NOT()

@codegens(ast.ID)
def codegen(self, c):
    c.LOAD_FAST(self.name)

@codegens(ast.Integer)
@codegens(ast.Boolean)
def codegen(self, c):
    c.LOAD_CONST(self.value())

@codegens(ast.Null)
def codegen(self, c):
    c.LOAD_CONST(None)

def wrapModule(path, code):
    c = CodeGen(path, 'module')
    #make main function
    c.LOAD_CONST(code)
    c.MAKE_FUNCTION()
    c.STORE_NAME('main')

    #ifmain
    c.LOAD_NAME('__name__')
    c.LOAD_CONST('__main__')
    c.COMPARE_OP(CmpOp.EQUAL)
    #c.POP_JUMP_IF_FALSE()
    c.POP_TOP()
    c.LOAD_NAME('main')
    c.CALL_FUNCTION()
    c.POP_TOP()

    #module return
    c.LOAD_CONST(None)
    c.RETURN_VALUE()

    return c

def codegen(path, tree):
    c = CodeGen(path, 'main')
    #actual generated code will go here
    c.setLine(1)
    tree.codegen(c)

    c.LOAD_CONST(None)
    c.RETURN_VALUE()

    mod = wrapModule(path, c)
    co = mod.code()
    with open(path, 'wb') as fout:
        #magic header
        fout.write(imp.get_magic())
        #timestamp
        fout.write(struct.pack('I', int(time.time())))
        #code object
        marshal.dump(co, fout)

def main():
    argParser = argparse.ArgumentParser(description='compile some MiniJava')
    argParser.add_argument('inputFile', nargs='?', type=InputFile)
    args = argParser.parse_args()
    if not args:
        return

    inputFile = args.inputFile
    if not inputFile:
        inputFile = sys.stdin

    import lexer
    import parser

    with inputFile as f:
        s = f.read()
        scanner = lexer.MiniJavaScanner()
        tokens = scanner.tokenize(s)

        programParser = parser.ProgramParser()
        tree = programParser.parse(tokens)

        parser.dump(tree)

        codegen('testmod.pyc', tree)

    import testmod

if __name__ == '__main__':
    main()

