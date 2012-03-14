#!/usr/bin/python

from array import array
from types import CodeType as Code
import dis

'''
BINARY_ADD:     23
BINARY_AND:     64
BINARY_FLOOR_DIVIDE:    26
BINARY_LSHIFT:  62
BINARY_MODULO:  22
BINARY_MULTIPLY:        20
BINARY_OR:      66
BINARY_POWER:   19
BINARY_RSHIFT:  63
BINARY_SUBSCR:  25
BINARY_SUBTRACT:        24
BINARY_TRUE_DIVIDE:     27
BINARY_XOR:     65
BREAK_LOOP:     80
BUILD_LIST:     103
BUILD_MAP:      105
BUILD_SET:      104
BUILD_SLICE:    133
BUILD_TUPLE:    102
CALL_FUNCTION:  131
CALL_FUNCTION_KW:       141
CALL_FUNCTION_VAR:      140
CALL_FUNCTION_VAR_KW:   142
COMPARE_OP:     107
CONTINUE_LOOP:  119
DELETE_ATTR:    96
DELETE_DEREF:   138
DELETE_FAST:    126
DELETE_GLOBAL:  98
DELETE_NAME:    91
DELETE_SUBSCR:  61
DUP_TOP:        4
DUP_TOP_TWO:    5
END_FINALLY:    88
EXTENDED_ARG:   144
FOR_ITER:       93
GET_ITER:       68
IMPORT_FROM:    109
IMPORT_NAME:    108
IMPORT_STAR:    84
INPLACE_ADD:    55
INPLACE_AND:    77
INPLACE_FLOOR_DIVIDE:   28
INPLACE_LSHIFT: 75
INPLACE_MODULO: 59
INPLACE_MULTIPLY:       57
INPLACE_OR:     79
INPLACE_POWER:  67
INPLACE_RSHIFT: 76
INPLACE_SUBTRACT:       56
INPLACE_TRUE_DIVIDE:    29
INPLACE_XOR:    78
JUMP_ABSOLUTE:  113
JUMP_FORWARD:   110
JUMP_IF_FALSE_OR_POP:   111
JUMP_IF_TRUE_OR_POP:    112
LIST_APPEND:    145
LOAD_ATTR:      106
LOAD_BUILD_CLASS:       71
LOAD_CLOSURE:   135
LOAD_CONST:     100
LOAD_DEREF:     136
LOAD_FAST:      124
LOAD_GLOBAL:    116
LOAD_NAME:      101
MAKE_CLOSURE:   134
MAKE_FUNCTION:  132
MAP_ADD:        147
NOP:            9
POP_BLOCK:      87
POP_EXCEPT:     89
POP_JUMP_IF_FALSE:      114
POP_JUMP_IF_TRUE:       115
POP_TOP:        1
PRINT_EXPR:     70
RAISE_VARARGS:  130
RETURN_VALUE:   83
ROT_THREE:      3
ROT_TWO:        2
SETUP_EXCEPT:   121
SETUP_FINALLY:  122
SETUP_LOOP:     120
SETUP_WITH:     143
SET_ADD:        146
STOP_CODE:      0
STORE_ATTR:     95
STORE_DEREF:    137
STORE_FAST:     125
STORE_GLOBAL:   97
STORE_LOCALS:   69
STORE_MAP:      54
STORE_NAME:     90
STORE_SUBSCR:   60
UNARY_INVERT:   15
UNARY_NEGATIVE: 11
UNARY_NOT:      12
UNARY_POSITIVE: 10
UNPACK_EX:      94
UNPACK_SEQUENCE:        92
WITH_CLEANUP:   81
YIELD_VALUE:    86
'''

class Flags:
    OPTIMIZED   = 0x0001
    NEWLOCALS   = 0x0002
    VARARGS     = 0x0004
    VARKEYWORDS = 0x0008
    NESTED      = 0x0010
    GENERATOR   = 0x0020
    NOFREE      = 0x0040

class Ops:
    for op in dis.opmap:
        locals()[op] = dis.opmap[op]

class CodeGen:
    co_name='<javapyc>'
    co_freevars = ()
    co_cellvars = ()
    co_argcount = 0

    def __init__(self, filename):
        self.co_names = []
        self.co_varnames = []
        self.co_nlocals = 0
        self.co_consts = [None]
        self.co_code = array('B')
        self.co_lnotab = array('B')
        self.co_firstlineno = 0
        self.co_filename = filename
        self.co_flags = Flags.OPTIMIZED | Flags.NOFREE
        self.co_stacksize = 0
        self._stacksize = 0
        self._lineno = None
        self._codeofs = 0

    def code(self):
        co_consts = list(self.co_consts)
        for i, const in enumerate(co_consts):
            if isinstance(const, CodeGen):
                co_consts[i] = const.code()
        return Code(self.co_argcount, len(self.co_varnames),
                    self.co_nlocals, self.co_stacksize, 
                    self.co_flags, self.co_code.tostring(), 
                    tuple(co_consts), tuple(self.co_names),
                    tuple(self.co_varnames), self.co_filename,
                    self.co_name, self.co_firstlineno, 
                    self.co_lnotab.tostring(), self.co_freevars,
                    self.co_cellvars)

    def setLine(self, line):
        if not self._lineno:
            self.co_firstlineno = line
            self._lineno = line
            return

        dLine = line - self._lineno
        dOfs = len(self.co_code) - self._codeofs

        #TODO handle larger cases

        if (dLine or dOfs) and dLine <= 255 and dOfs <= 255:
            self.co_lnotab.append(dOfs)
            self.co_lnotab.append(dLine)

        self._lineno = line
        self._codeofs = len(self.co_code)

    def getName(self, name):
        if name not in self.co_names:
            self.co_names.append(name)
        index = self.co_names.index(name)
        return index

    def write(self, op, value=None):
        self.co_code.append(op)
        if value != None:
            self.co_code.append(value & 0xFF)
            self.co_code.append((value>>8) & 0xFF)

    def LOAD_CONST(self, value):
        if value not in self.co_consts:
            self.co_consts.append(value)
        index = self.co_consts.index(value)
        self.write(Ops.LOAD_CONST, index)
        self.pushStack()

    def LOAD_NAME(self, value):
        index = self.getName(value)
        self.write(Ops.LOAD_NAME, index)
        self.pushStack()
    
    def STORE_NAME(self, value):
        index = self.getName(value)
        self.write(Ops.STORE_NAME, index)
        self.popStack()
    
    def POP_TOP(self):
        self.write(Ops.POP_TOP)
        self.popStack()
    
    def MAKE_FUNCTION(self, defaults=0):
        self.write(Ops.MAKE_FUNCTION, defaults)
        self.popStack(1+defaults)
        self.pushStack()

    def CALL_FUNCTION(self, argc=0):
        self.write(Ops.CALL_FUNCTION)
        self.co_code.append(argc)
        self.co_code.append(0)
        self.popStack(argc+1)
        self.pushStack()

    def RETURN_VALUE(self):
        self.write(Ops.RETURN_VALUE)
        self.popStack()

    def BINARY_ADD(self):
        self.write(Ops.BINARY_ADD)
        self.popStack(2)
        self.pushStack(1)

    def popStack(self, n=1):
        self._stacksize -= n
        if self._stacksize < 0:
            raise AssertionError('Stack Underflow')

    def pushStack(self, n=1):
        self._stacksize += n
        self.co_stacksize = max(self.co_stacksize, self._stacksize)

def main():
    import imp
    import marshal
    import time
    import struct

    t = CodeGen("testmod.java")
    #actual generated code will go here
    t.setLine(1)
    t.LOAD_NAME('print')
    t.LOAD_CONST(5)
    t.LOAD_CONST(42-5)
    t.BINARY_ADD()
    t.CALL_FUNCTION(1)
    t.POP_TOP()

    t.LOAD_CONST(None)
    t.RETURN_VALUE()


    c = CodeGen("testmod.java")
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

    co = c.code()
    with open('testmod.pyc', 'wb') as fout:
        #magic header
        fout.write(imp.get_magic())
        #timestamp
        fout.write(struct.pack('I', int(time.time())))
        #code object
        marshal.dump(co, fout)
    import testmod

if __name__ == '__main__':
    main()
