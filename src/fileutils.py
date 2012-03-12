import sys
import os
from tempfile import mkstemp

class InputFile:
    def __init__(self, path):
        self.path = path
        self.f = None
    def get(self):
        return self.f
    def __enter__(self):
        if self.path == '-':
            self.f = sys.stdin
        else:
            self.f = open(self.path)
        return self.f
    def __exit__(self, *exc_info):
        if self.path != '-' and self.f != None:
            self.f.close()
        self.f = None
    def __repr__(self):
        return "InputFile('{0}')".format(self.path)

class TempFile:
    def __init__(self):
        fd, self.name = mkstemp()
        self.f = open(fd, 'w+')
    def __enter__(self):
        return self
    def flush(self):
        self.f.flush()
    def __exit__(self, *exc_info):
        self.f.close()
        self.f = None
        os.remove(self.name)
