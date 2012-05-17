#!/usr/bin/python3

import os
import os.path
import sys
import re
import time
import unittest
import subprocess
from glob import iglob as glob
from util import staticinit

import spark
import lexer
import parser
import typechecker
import optimizer
import codegen

from fileutils import TempFile

def testFiles(ext):
    data = list(os.walk('tests'))
    data.sort(key=lambda l: l[0])
    for subdir, subdirs, files in data:
        prefix = subdir + '/'
        for filepath in sorted(files):
            pref, e = os.path.splitext(filepath)
            expected = pref + '.' + ext 
            if e == '.java' and expected in files:
                name = 'test_' + re.sub('\W', '_', (prefix+pref)[6:])
                yield name, prefix+filepath, prefix+expected

class FileTest(unittest.TestCase):

    def diff(self, expected, actual):
        proc = subprocess.Popen(('diff', actual, expected))
        res = proc.wait()
        self.assertEqual(0, res)

@staticinit
class LexerTests(FileTest):

    @classmethod
    def __static__(cls):
        for name, p, expected in testFiles('lexout'):
            def makeTest(p, expected):
                def runTest(self):
                    scanner = lexer.MiniJavaScanner()
                    with open(p) as f: s = f.read()
                    tokens = scanner.tokenize(s)
                    with TempFile() as fout:
                        lexer.dump(tokens, fout.f)
                        fout.flush()
                        self.diff(expected, fout.name)
                return runTest
            setattr(cls, name, makeTest(p, expected))

    def test_errors(self):
        p = 'tests/errors.java'
        scanner = lexer.MiniJavaScanner()
        with open(p) as f: s = f.read()

        with self.assertRaises(spark.LexerException):
            scanner.tokenize(s)

@staticinit
class ParserTests(FileTest):

    @classmethod
    def __static__(cls):
        for name, p, expected in testFiles('parseout'):
            def makeTest(p, expected):
                def runTest(self):
                    scanner = lexer.MiniJavaScanner()
                    with open(p) as f: s = f.read()
                    tokens = scanner.tokenize(s)
                    javaParser = parser.ProgramParser()
                    tree = javaParser.parse(tokens)
                    with TempFile() as fout:
                        parser.dump(tree, fout.f)
                        fout.flush()
                        self.diff(expected, fout.name)
                return runTest
            setattr(cls, name, makeTest(p, expected))


    def checkError(self, p):
        scanner = lexer.MiniJavaScanner()
        with open(p) as f: s = f.read()
        tokens = scanner.tokenize(s)
        javaParser = parser.ProgramParser()
        with self.assertRaises(spark.ParserException):
            javaParser.parse(tokens)

    def test_errors(self):
        p = 'tests/simple_parseerror.java'
        self.checkError(p)

class CodegenTests(FileTest):
    @classmethod
    def init(cls, optimize=0, skip=[]):
        for name, p, expected in testFiles('out'):
            def makeTest(name, p, expected):
                def runTest(self):
                    scanner = lexer.MiniJavaScanner()
                    with open(p) as f: s = f.read()
                    tokens = scanner.tokenize(s)
                    javaParser = parser.ProgramParser()
                    tree = javaParser.parse(tokens)
                    typechecker.typecheck(tree)
                    if optimize:
                        for roundNum in range(optimize):
                            tree.optimize()
                    binpath = os.path.join('testbins', name + '.pyc')
                    codegen.codegen(binpath, tree, False)
                    with TempFile() as fout:
                        #run program
                        proc = subprocess.Popen(('python3', binpath),
                                                stdout=fout.f,
                                                stderr=subprocess.STDOUT)

                        #let the process run for a few seconds
                        failTime = time.time() + 3.0
                        while proc.poll() is None:
                            time.sleep(0.01)
                            if time.time() > failTime:
                                proc.kill()
                                raise Exception('Compiled program took too long to execute')

                        res = proc.wait()
                        self.assertEqual(0, res)
                        fout.flush()
                        self.diff(expected, fout.name)
                return runTest
            if name not in skip:
                setattr(cls, name, makeTest(name, p, expected))

@staticinit
class FastgenTests(CodegenTests):
    @classmethod
    def setUpClass(cls):
        import fastgen
        subprocess.call(['rm', '-rf', 'testbins'])
        subprocess.call(['mkdir', 'testbins'])
    @classmethod
    def __static__(cls):
        cls.init()

@staticinit
class OptimizerTests(CodegenTests):
    @classmethod
    def setUpClass(cls):
        import fastgen
        subprocess.call(['rm', '-rf', 'testbins'])
        subprocess.call(['mkdir', 'testbins'])
    @classmethod
    def __static__(cls):
        cls.init(5, skip=['test_generator'])

@staticinit
class SlowgenTests(CodegenTests):
    @classmethod
    def setUpClass(cls):
        import slowgen
        subprocess.call(['rm', '-rf', 'testbins'])
        subprocess.call(['mkdir', 'testbins'])
    @classmethod
    def __static__(cls):
        cls.init(skip=['test_generator', 'test_strings'])

if __name__ == '__main__':
    unittest.main()

