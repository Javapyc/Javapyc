#!/usr/bin/python

from spark import *
from fileutils import InputFile
import argparse
import sys

class Token:
    def __str__(self):
        return '({0}, {1})'.format(self.__class__.__name__, self.getToken())
    def typename(self):
        return self.__class__.__name__

class SimpleToken(Token):
    def __init__(self, val):
        self.val = val
    def getToken(self):
        return str(self.val)

class Whitespace(SimpleToken):
    pass

class Integer(SimpleToken):
    pass

class Delimiter(SimpleToken):
    def typename(self):
        return self.val

class Operator(Token):
    def __init__(self, op):
        self.op = op
    def getToken(self):
        return str(self.op)
    def typename(self):
        return self.op

class ExpressionScanner(GenericScanner):
    def __init__(self):
        GenericScanner.__init__(self)
        
    def tokenize(self, s):
        self.rv = []
        GenericScanner.tokenize(self, s)
        return self.rv
    
    def t_whitespace(self, s):
        r'\s+'
        pass

    def t_integer(self, s):
        r'[1-9]\d*|0'
        t = Integer(int(s))
        self.rv.append(t)

    def t_operator(self, s):
        r'\+|\-|\*'
        t = Operator(s)
        self.rv.append(t)
    
    def t_delimiter(self, s):
        r'{|}|\(|\)|\[|\]|;|='
        t = Delimiter(s)
        self.rv.append(t)

def dump(tokens):
    for token in tokens:
        print(token)

def main():
    parser = argparse.ArgumentParser(description='lex some MiniJava')
    parser.add_argument('files', nargs='+', type=InputFile)
    args = parser.parse_args()
    if not args:
        return

    for inputFile in args.files:
        with inputFile as f:
            s = f.read()
            scanner = ExpressionScanner()
            for token in scanner.tokenize(s):
                print(token)

if __name__ == '__main__':
    main()

