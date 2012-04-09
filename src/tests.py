#!/usr/bin/python3

import os
import os.path
import sys
import re
import unittest
import lexer
import subprocess
from glob import iglob as glob
from util import staticinit
import spark

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
class LexerTest(FileTest):

    @classmethod
    def __static__(cls):
        for name, p, expected in testFiles('out'):
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


if __name__ == '__main__':
    unittest.main()

