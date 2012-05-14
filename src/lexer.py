#!/usr/bin/python

from spark import *
from fileutils import InputFile
import argparse
import sys

class Token:
    def __str__(self):
        return '{0}, {1}'.format(self.__class__.__name__, self.getToken())
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

class String(SimpleToken):
    def __init__(self, val):
        val = val[1:-1]
        def unescape(s):
            s = s.replace('\\n', '\n')
            s = s.replace('\\\\', '\\')
            s = s.replace('\\"', '"')
            return s
        self.val = unescape(val)
    def typename(self):
        return 'StringLiteral'

class ID(SimpleToken):
    pass

class Delimiter(SimpleToken):
    def typename(self):
        return self.val

class ReservedWord(SimpleToken):
    def typename(self):
        return self.val

class Operator(Token):
    def __init__(self, op):
        self.op = op
    def getToken(self):
        return str(self.op)
    def typename(self):
        return self.op

class ExpressionScanner1(GenericScanner):
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
        r'[1-9]\d*\b|0\b'
        t = Integer(int(s))
        self.rv.append(t)

    def t_delimiter(self, s):
        r':|;|\.|,|=|\(|\)|{|}|\[|\]'
        t = Delimiter(s)
        self.rv.append(t)

    def t_ID(self, s):
        r'[a-zA-Z](\w|\d)*'
        t = ID(s)
        self.rv.append(t)

class ExpressionScanner2(ExpressionScanner1):
    ''' Do this so that reserved words are checked first '''

    # Need to be checked first or will be considered an ID
    def t_reserved(self, s):
        r'class\b|public\b|static\b|extends\b|void\b|int\b|boolean\b|if\b|else\b|while\b|for\b|return\b|null\b|true\b|false\b|this\b|new\b|String\.format\b|String\b|main\b|System\.out\.printf\b|System\.out\.println\b|Math.pow\b|break\b|yield\b'
        t = ReservedWord(s)
        self.rv.append(t)

    def t_string(self, s):
        r'"(\\.|.)*?"'
        t = String(s)
        self.rv.append(t)

    # This needs to be checked before t_delimiter - because of the ==
    def t_operator(self, s):
        r'\+|\-|\*|/|<|>|==|\&\&|\|\||\!'
        t = Operator(s)
        self.rv.append(t)

class MiniJavaScanner(ExpressionScanner2):
    # Does this need to be checked before the / operator? Probably. 
    def t_comment(self, s):
        r'(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)'
        pass

    def t_operator_prec(self, s):
        r'<=|>=|\!='
        t = Operator(s)
        self.rv.append(t)
    

def dump(tokens, outfile):
    for token in tokens:
        print(token, file=outfile)

def main():
    parser = argparse.ArgumentParser(description='lex some MiniJava')
    parser.add_argument('files', nargs='+', type=InputFile)
    args = parser.parse_args()
    if not args:
        return

    for inputFile in args.files:
        with inputFile as f:
            s = f.read()
            scanner = MiniJavaScanner()
            for token in scanner.tokenize(s):
                print(token)

if __name__ == '__main__':
    main()

