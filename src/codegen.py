#!/usr/bin/python3

from code import CodeGen, CmpOp, Flags
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
    
    #codegen classes
    for cls in classes:
        cls.codegen(c)

    #make main function
    main = CodeGen(c.filename, 'main')
    main.context = mainclass.context
    main.setFlags(Flags.NEWLOCALS | Flags.OPTIMIZED)
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

@codegens(ast.ClassDecl)
def codegen(self, c):
    c.LOAD_BUILD_CLASS()

    cls = CodeGen(c.filename, self.name)
    cls.setFlags(Flags.NEWLOCALS)
    cls.argcount = 1
    cls.setLine(1)
    cls.LOAD_FAST('__locals__')
    cls.STORE_LOCALS()
    cls.LOAD_NAME('__name__')
    cls.STORE_NAME('__module__')

    #define constructor to initialize class variables
    init = CodeGen(cls.filename, '__init__')
    init.setFlags(Flags.NEWLOCALS | Flags.OPTIMIZED)
    init.argcount = 1
    init.varnames = ['self']
    if self.parent:
        init.LOAD_GLOBAL(self.parent)
        init.LOAD_ATTR('__init__')
        init.LOAD_FAST('self')
        init.CALL_FUNCTION(1)
        init.POP_TOP()

    for var in self.classvars:
        vartype = var.typename
        if vartype == ast.IntType:
            init.LOAD_CONST(0)
        elif vartype == ast.BoolType:
            init.LOAD_CONST(False)
        else:
            init.LOAD_CONST(None)
        init.LOAD_FAST('self')
        init.STORE_ATTR(var.ID)
    init.LOAD_CONST(None)
    init.RETURN_VALUE()
    cls.LOAD_CONST(init)
    cls.MAKE_FUNCTION()
    cls.STORE_NAME('__init__')

    #generate methods
    for method in self.children:
        func = CodeGen(cls.filename, method.ID)
        func.context = method.context
        func.setFlags(Flags.NEWLOCALS | Flags.OPTIMIZED)
        func.argcount = len(method.formallist) + 1
        func.varnames = ['self'] + list(map(lambda formal: formal.ID, method.formallist))
        method.codegen(func)
        cls.LOAD_CONST(func)
        cls.MAKE_FUNCTION()
        cls.STORE_NAME(method.ID)

    cls.LOAD_CONST(None)
    cls.RETURN_VALUE()

    c.LOAD_CONST(cls)
    c.MAKE_FUNCTION()

    c.LOAD_CONST(self.name)
    if self.parent:
        c.LOAD_GLOBAL(self.parent)
        c.CALL_FUNCTION(3)
    else:
        c.CALL_FUNCTION(2)
    c.STORE_NAME(self.name)

@codegens(ast.MethodDecl)
def codegen(self, c):
    c.setLine(1)
    *stmts, expr = self.children
    for stmt in stmts:
        stmt.codegen(c)
    expr.codegen(c)
    c.RETURN_VALUE()

@codegens(ast.MethodCall)
def codegen(self, c):
    (call,) = self.children

    call.codegen(c)
    c.POP_TOP()

@codegens(ast.StmtList)
def codegen(self, c):
    stmts = self.children
    for s in stmts:
        s.codegen(c)

@codegens(ast.Decl)
def codegen(self, c):
    (expr,) = self.children
    expr.codegen(c)
    
    context = c.context
    classContext = context.classContext
    typename = classContext.varType(self.name)
    if typename:
        c.LOAD_FAST('self')
        c.STORE_ATTR(self.name)
    else:
        c.STORE_FAST(self.name)

@codegens(ast.Assignment)
def codegen(self, c):
    (expr,) = self.children
    expr.codegen(c)
    
    context = c.context
    classContext = context.classContext
    typename = classContext.varType(self.name)
    if typename:
        c.LOAD_FAST('self')
        c.STORE_ATTR(self.name)
    else:
        c.STORE_FAST(self.name)

@codegens(ast.Print)
def codegen(self, c):
    (expr,) = self.children
    c.LOAD_GLOBAL('print')
    expr.codegen(c)
    c.CALL_FUNCTION(1)
    c.POP_TOP()

@codegens(ast.Printf)
def codegen(self, c):
    args = self.children
    c.LOAD_GLOBAL('print')
    c.LOAD_CONST(self.string)
    if len(args):
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

@codegens(ast.NewInstance)
def codegen(self, c):
    c.LOAD_GLOBAL(self.name)
    c.CALL_FUNCTION()

@codegens(ast.Boolean)
@codegens(ast.Integer)
def codegen(self, c):
    c.LOAD_CONST(self.value())

@codegens(ast.Null)
def codegen(self, c):
    c.LOAD_CONST(None)

@codegens(ast.This)
def codegen(self, c):
    c.LOAD_FAST('self')

@codegens(ast.ID)
def codegen(self, c):
    context = c.context
    classContext = context.classContext
    typename = classContext.varType(self.name)
    if typename:
        c.LOAD_FAST('self')
        c.LOAD_ATTR(self.name)
    else:
        c.LOAD_FAST(self.name)

@codegens(ast.Pow)
def codegen(self, c):
    a, b = self.children
    a.codegen(c)
    b.codegen(c)
    c.BINARY_POWER()

@codegens(ast.Call)
def codegen(self, c):
    obj, *args = self.children
    func = self.func

    obj.codegen(c)
    c.LOAD_ATTR(func)

    for arg in args:
        arg.codegen(c)

    c.CALL_FUNCTION(len(args))

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
        dump(co)

def dump(co, indent=0):
    import dis
    import types
    def pprint(text, extra=0):
        for i in range(indent+extra):
            print('  ', end='')
        print(text)
    pprint("co_name:\t{0}".format(co.co_name))
    for key in dir(co):
        if not key.startswith('co_'):
            continue
        if key in ['co_name', 'co_code', 'co_lnotab']:
            continue
        elif key == 'co_consts':
            pprint("{0}:".format(key))
            for v in co.co_consts:
                if type(v) == types.CodeType:
                    pprint('- Code Object:')
                    dump(v, indent+1)
                else:
                    pprint('- {0}'.format(v))
        elif key == 'co_flags':
            val = dis.pretty_flags(co.co_flags)
            pprint("{0}:\t\t{1}".format(key, val))
        else:
            val = getattr(co, key)
            pprint("{0}:\t{1}".format(key, val))
    #doesn't obey indent level
    dis.dis(co)

