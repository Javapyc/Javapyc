#!/usr/bin/python

import lexer
import parser
import typechecker
import optimizer
import codegen

from fileutils import InputFile
import argparse
import sys

def getArguments():
    parser = argparse.ArgumentParser(description='MiniJava Compiler')
    parser.add_argument('--phase', '-p', choices=('lex', 'parse', 'typecheck', 'optimize', 'codegen', 'run'), default='run')
    parser.add_argument('--out-file', '-o', type=str, default='a')
    parser.add_argument('--verbose', '-v', action='count')
    parser.add_argument('--optimize', '-O', action='store_true', help='enable optimizations')
    parser.add_argument('files', nargs='+', type=InputFile)
    return parser.parse_args()

def main():
    args = getArguments()
    if not args:
        sys.exit(1)
    if len(args.files) > 1:
        print("Only one input file is supported")
        sys.exit(1)

    if args.phase == 'optimize':
        args.optimize = True

    outfile = args.out_file + '.pyc'
    verbose = args.verbose

    for inputFile in args.files:
        with inputFile as f:
            s = f.read()

            #Lexical Analysis
            scanner = lexer.MiniJavaScanner()
            tokens = scanner.tokenize(s)
            if args.phase == 'lex':
                lexer.dump(tokens, sys.stdout)
                break

            #Parsing
            p = parser.ProgramParser()
            tree = p.parse(tokens)
            if args.phase == 'parse':
                parser.dump(tree, sys.stdout)
                break
            
            #Typecheck Parse Tree
            try:
                typechecker.typecheck(tree)
            except typechecker.TypecheckException as ex:
                print('Nope', file=sys.stderr)
                if verbose:
                    print(ex, file=sys.stderr)
                    if verbose > 1:
                        raise ex
                sys.exit(1)
            if args.phase == 'typecheck':
                print('Looks good')
                break
            
            #Optimization
            if args.phase == 'optimize':
                parser.dump(tree)
                print()
            if args.optimize:
                tree.optimize()
            if args.phase == 'optimize':
                parser.dump(tree)
                break
            
            #Generate Code
            codegen.codegen(outfile, tree)
            if args.phase == 'codegen':
                break

            if args.phase == 'run':
                import importlib
                importlib.import_module(args.out_file)

if __name__ == '__main__':
    main()

