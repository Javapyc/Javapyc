#!/usr/bin/python

# -----------------------------------------------------------------------------
# calc.py
#
# A simple calculator with variables -- all in one file.
# -----------------------------------------------------------------------------

from lexer import lex
from parser import yacc

while 1:
    try:
        s = input('calc > ')   # Use raw_input on Python 2
    except EOFError:
        break
    lexer = lex.input(s)
    for tok in iter(lex.token, None):
        print("({0}, {1})".format(tok.type, tok.value))
    print("Result: ", end='')
    yacc.parse(s)

