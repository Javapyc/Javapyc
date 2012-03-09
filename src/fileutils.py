import sys

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

