#!/usr/bin/python3

from code import CodeGen
import parser

import imp
import marshal
import time
import struct

from fileutils import InputFile
import argparse
import sys

def wrapModule(path, code):
    c = CodeGen(path)
    #make main function
    c.LOAD_CONST(code)
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
    c = CodeGen(path)
    #actual generated code will go here
    c.setLine(1)
    tree.codegen(c)

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

def main():
    parser = argparse.ArgumentParser(description='compile some MiniJava')
    parser.add_argument('inputFile', nargs='?', type=InputFile)
    args = parser.parse_args()
    if not args:
        return

    inputFile = args.inputFile
    if not inputFile:
        inputFile = sys.stdin

    import lexer
    import parser

    with inputFile as f:
        s = f.read()
        scanner = lexer.ExpressionScanner()
        tokens = scanner.tokenize(s)

        programParser = parser.ProgramParser()
        tree = programParser.parse(tokens)

        parser.dump(tree)

        codegen('test', tree)

    import testmod

if __name__ == '__main__':
    main()
