
def staticinit(cls):
    '''
    Runs a static initializer on a class.
    Requires a classmethod called __static__ to be defined.
    '''
    cls.__static__()
    return cls

