#!/usr/bin/python

import lexer
import parser

from fileutils import InputFile
import argparse
import sys

def getArguments():
    parser = argparse.ArgumentParser(description='MiniJava Compiler')
    parser.add_argument('--phase', '-p', choices=('lex', 'parse', 'typecheck', 'codegen'), default='codegen')
    parser.add_argument('files', nargs='+', type=InputFile)
    return parser.parse_args()

def main():
    args = getArguments()
    if not args:
        return

    for inputFile in args.files:
        with inputFile as f:
            s = f.read()

            #Lexical Analysis
            scanner = lexer.ExpressionScanner()
            tokens = scanner.tokenize(s)
            if args.phase == 'lex':
                lexer.dump(tokens)
                break

            #Parsing
            p = parser.ExprParser()
            tree = p.parse(tokens)
            if args.phase == 'parse':
                parser.dump(tree)
                break
            
            #Typecheck Parse Tree
            if args.phase == 'typecheck':
                break
            
            #Generate Code
            if args.phase == 'codegen':
                break

if __name__ == '__main__':
    main()

