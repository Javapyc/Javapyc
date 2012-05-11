#!/usr/bin/python3

from code import CodeGen, CmpOp, Flags
import ast
import settings

import imp
import marshal
import time
import struct

def codegens(cls):
    '''
    Annotates a function that will be added to the given class
    that can generate code for itself
    '''
    def wrap(func):
        setattr(cls, 'codegen', func)
        return func
    return wrap

#include specialized codegen routines
if settings.MODE_FASTGEN:
    import fastgen
else:
    import slowgen

#include common codegen routines
@codegens(ast.Print)
def codegen(self, c):
    (expr,) = self.children
    c.LOAD_GLOBAL('print')
    expr.codegen(c)
    c.CALL_FUNCTION(1)
    c.POP_TOP()

@codegens(ast.FormatString)
def codegen(self, c):
    args = self.children
    c.LOAD_CONST(self.string)
    if len(args):
        for arg in args:
            if isinstance(arg.nodeType, ast.BaseObjectType):
                arg.codegen(c)
                c.LOAD_ATTR('__str__')
                c.CALL_FUNCTION()
            else:
                arg.codegen(c)
        c.BUILD_TUPLE(len(args))
        c.BINARY_MODULO()

@codegens(ast.Printf)
def codegen(self, c):
    (formatString,) = self.children
    c.LOAD_GLOBAL('print')
    formatString.codegen(c)
    c.LOAD_CONST('end')
    c.LOAD_CONST('')
    c.CALL_FUNCTION(1, 1)
    c.POP_TOP()

@codegens(ast.MethodCall)
def codegen(self, c):
    (call,) = self.children

    call.codegen(c)
    c.POP_TOP()

@codegens(ast.Or)
def codegen(self, c):
    ''' Handle short circuiting 'or' statements '''
    left, right = self.children
    left.codegen(c)
    mark = c.JUMP_IF_TRUE_OR_POP()
    right.codegen(c)
    c.popStack(1)
    mark()

@codegens(ast.And)
def codegen(self, c):
    ''' Handle short circuiting 'and' statements '''
    left, right = self.children
    left.codegen(c)
    mark = c.JUMP_IF_FALSE_OR_POP()
    right.codegen(c)
    c.popStack(1)
    mark()

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
    c.LOAD_GLOBAL('int')
    self.left.codegen(c)
    self.right.codegen(c)
    c.BINARY_TRUE_DIVIDE()
    c.CALL_FUNCTION(1)

@codegens(ast.Negate)
def codegen(self, c):
    (expr,) = self.children
    expr.codegen(c)
    c.UNARY_NEGATIVE()

@codegens(ast.Not)
def codegen(self, c):
    (expr,) = self.children
    expr.codegen(c)
    c.UNARY_NOT()

@codegens(ast.Boolean)
@codegens(ast.Integer)
def codegen(self, c):
    c.LOAD_CONST(self.value())

@codegens(ast.Null)
def codegen(self, c):
    c.LOAD_CONST(None)

@codegens(ast.Pow)
def codegen(self, c):
    a, b = self.children
    a.codegen(c)
    b.codegen(c)
    c.BINARY_POWER()
 
@codegens(ast.StringFormat)
def codegen(self, c):
    (formatString,) = self.children
    formatString.codegen(c)

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

