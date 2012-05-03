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
    
    c.setLine(1)
    
    #TODO codegen classes

    #make main function
    main = CodeGen(c.filename, 'main')
    mainclass.codegen(main)
    c.LOAD_CONST(main)
    c.MAKE_FUNCTION()
    c.STORE_NAME('main')

    #ifmain
    c.LOAD_NAME('__name__')
    c.LOAD_CONST('__main__')
    c.COMPARE_OP(CmpOp.EQUAL)
    dest = c.POP_JUMP_IF_FALSE()
    c.LOAD_NAME('main')
    c.CALL_FUNCTION()
    c.POP_TOP()

    #module return
    dest()
    c.LOAD_CONST(None)
    c.RETURN_VALUE()

@codegens(ast.MainClassDecl)
def codegen(self, c):
    c.setLine(1)
    stmts = self.children
    for stmt in stmts:
        stmt.codegen(c)
    
    #return null;
    c.LOAD_CONST(None)
    c.RETURN_VALUE()

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
    jumpLoc = c.POP_JUMP_IF_FALSE()

    # Codegen the ifstmt
    ifstmt.codegen(c)

    # Skip the else block
    endOfIf = c.JUMP_FORWARD()

    # Mark the jump to the else block
    jumpLoc()

    # Codegen the else stmt
    elsestmt.codegen(c)

    # Mark the end of the if statement
    endOfIf()
    
@codegens(ast.While)
def codegen(self, c):
    cond, stmt = self.children

    # Store the place to jump back to
    beforeCond = c.marker()

    # Codegen the condition
    cond.codegen(c)

    # Write the jump instruction
    jumpLoc = c.POP_JUMP_IF_FALSE()

    # Codegen the stmt
    stmt.codegen(c)

    # Jump back to before the cond
    c.JUMP_ABSOLUTE(beforeCond)

    # Mark the end of the while loop
    jumpLoc()


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


def codegen(path, tree, dumpbin = False):
    module = CodeGen(path, '<module>')
    tree.codegen(module)
    co = module.code()

    with open(path, 'wb') as fout:
        #magic header
        fout.write(imp.get_magic())
        #timestamp
        fout.write(struct.pack('I', int(time.time())))
        #code object
        marshal.dump(co, fout)

    if dumpbin:
        import dis
        dis.disco(module)

