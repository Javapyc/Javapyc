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

#TODO: ClassDecl
#TODO: MethodDecl
#TODO: Type
#TODO: MethodCall
#TODO: Stmtlist

@codegens(ast.StmtList)
def codegen(self, c):
    stmts = self.children
    for s in stmts:
        s.codegen(c)


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
    c.LOAD_CONST('end')
    c.LOAD_CONST('')
    c.CALL_FUNCTION(1, 1)
    c.POP_TOP()

@codegens(ast.If)
def codegen(self, c):
    cond, ifstmt, elsestmt = self.children
    cond.codegen(c)

    # binary array size coincides with binary location of instructions
    jumpLoc = len(c.co_code) 
    c.POP_JUMP_IF_FALSE(0) # dummy value. Will set to beginning of else block

    # Codegen the ifstmt
    ifstmt.codegen(c)

    endOfIf = len(c.co_code)
    c.JUMP_FORWARD(0) # dummy value: jump to end of else block

    # Go back and set the first dummy value to the correct value
    # Note: this is an absolute address
    c.co_code[jumpLoc+1] = len(c.co_code)

    # Codegen the else stmt
    elsestmt.codegen(c)

    # Go back and set the second dummy value to the correct value
    # Note: this is a relative address, hence the -3 to account for off-by-one
    # FIXME: the -3 might be a problem? Is it always -3?
    c.co_code[endOfIf+1] = len(c.co_code) - endOfIf - 3 
    
@codegens(ast.While)
def codegen(self, c):
    cond, stmt = self.children

    # Store the place to jump back to
    beforeCond = len(c.co_code)

    # Codegen the condition
    cond.codegen(c)

    # Store the index of the jump instruction
    jumpLoc = len(c.co_code)

    # Write the jump instruction
    c.POP_JUMP_IF_FALSE(0)

    # Codegen the stmt
    stmt.codegen(c)

    # Jump back to before the cond
    c.JUMP_ABSOLUTE(beforeCond)

    # Go back and fix the target of the jump instruction
    # Note: it is jumpLoc +1 because co_code[jumpLoc]
    # actually refers to the opcode for the jump instruction.
    # We want to change the target (which is next in the
    # array), not the opcode. 
    c.co_code[jumpLoc+1] = len(c.co_code)


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

#FIXME: NewInstance
@codegens(ast.NewInstance)
def codegen(self, c):
    #s.LOAD_GLOBAL(self.name)
    c.LOAD_NAME(self.name)

@codegens(ast.Boolean)
@codegens(ast.Integer)
def codegen(self, c):
    c.LOAD_CONST(self.value())

@codegens(ast.Null)
def codegen(self, c):
    c.LOAD_CONST(None)

#TODO: This

@codegens(ast.ID)
def codegen(self, c):
    c.LOAD_FAST(self.name)

@codegens(ast.Pow)
def codegen(self, c):
    a, b = self.children
    a.codegen(c)
    b.codegen(c)
    c.BINARY_POWER()

#FIXME: Call
@codegens(ast.Call)
def codegen(self, c):
    obj, args = self.children
    func = self.func
    c.LOAD_FAST(obj)
    print(func)
    c.LOAD_ATTR(func)

    #for arg in args:
    args.codegen(c)


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

def codegen(path, tree, dumpbin = False):
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

    if dumpbin:
        import dis
        dis.disco(c)


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
    import dis
    dis.dis(testmod.main)

if __name__ == '__main__':
    main()

