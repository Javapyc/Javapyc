
MODE_PEDANTIC = False
MODE_FASTGEN = True
VERBOSITY = 0

class PedanticException(Exception):
    pass

def requireExtended():
    if MODE_PEDANTIC:
        raise PedanticException()

def shouldLog(level):
    return VERBOSITY >= level
