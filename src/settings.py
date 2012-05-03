
MODE_PEDANTIC = False
MODE_FASTGEN = True

class PedanticException(Exception):
    pass

def requireExtended():
    if MODE_PEDANTIC:
        raise PedanticException()

