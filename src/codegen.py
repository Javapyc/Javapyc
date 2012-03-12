#!/usr/bin/python

import code
import parser

import imp
import marshal
import time
import struct

def wrapModule(path, code):
    #FIXME name conflict: code
    c = code.CodeGen(path)
    def pr(s):
        #prints a message
        c.LOAD_NAME('print')
        c.LOAD_CONST(s)
        c.CALL_FUNCTION(1)
        c.POP_TOP()
    #make main function
    c.LOAD_CONST(t)
    c.MAKE_FUNCTION()
    c.STORE_NAME('main')

    #ifmain
    #c.LOAD_NAME('__name__')
    #c.LOAD_CONST('__main__')
    c.LOAD_NAME('main')
    c.CALL_FUNCTION()
    c.POP_TOP()

    #module return
    c.LOAD_CONST(None)
    c.RETURN_VALUE()

    return c

def codegen(path, tree):
    c = code.CodeGen(path)
    #actual generated code will go here
    c.setLine(1)
    c.LOAD_NAME('print')
    c.LOAD_CONST(5)
    c.LOAD_CONST(42-5)
    c.BINARY_ADD()
    c.CALL_FUNCTION(1)
    c.POP_TOP()

    c.LOAD_CONST(None)
    c.RETURN_VALUE()

    mod = wrapModule(path, c)
    co = mod.code()
    with open('testmod.pyc', 'wb') as fout:
        #magic header
        fout.write(imp.get_magic())
        #timestamp
        fout.write(struct.pack('I', int(time.time())))
        #code object
        marshal.dump(co, fout)

