#!/usr/bin/python3

import os.path
import sys
import unittest
import lexer
import subprocess
from glob import iglob as glob

from fileutils import TempFile

class FileTest(unittest.TestCase):

    def diff(self, expected, actual):
        proc = subprocess.Popen(('diff', actual, expected))
        res = proc.wait()
        self.assertEqual(0, res)

class LexerTest(FileTest):
    for p in glob('tests/*.java'):
        expected = os.path.splitext(p)[0] + ".lexout"
        if not os.path.exists(expected):
            continue

        def makeTest(p, expected):
            def runTest(self):
                scanner = lexer.ExpressionScanner()
                with open(p) as f: s = f.read()
                tokens = scanner.tokenize(s)
                with TempFile() as fout:
                    lexer.dump(tokens, fout.f)
                    fout.flush()
                    self.diff(expected, fout.name)
            return runTest
        name = 'test_' + p.split('.')[0].split('/')[1]
        locals()[name] = makeTest(p, expected)

    def test_errors(self):
        p = 'tests/errors.java'
        expected = 'tests/errors.lexout'
        scanner = lexer.ExpressionScanner()
        with open(p) as f: s = f.read()

        with self.assertRaises(LexerException):
            tokens.scanner.tokenize(s)


if __name__ == '__main__':
    unittest.main()

