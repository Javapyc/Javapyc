
class MethodPrototype:
    def __init__(self, name, params):
        self.name = name
        self.params = params
    def __eq__(self, o):
        return self.name == o.name and self.params == o.params
    def __hash__(self):
        return hash(self.name) + 683 * hash(self.params)

class ProgramContext:
    def __init__(self):
        self.classes = {}
    def registerClass(self, name, classContext):
        self.classes[name] = classContext
        classContext.program = self
    def lookupClass(self, name):
        return self.classes.get(name, None)

class ClassContext:
    def __init__(self, name, classvars, variables, methods, parent=None):
        self.name = name
        self.classvars = classvars
        self.variables = variables
        self.methods = methods
        self.parent = parent
        self.program = None
    def varType(self, name):
        res = self.variables.get(name, None)
        if not res and self.parent:
            return self.parent.varType(name)
        return res
    def lookupMethod(self, name, argTypes):
        def findMethod():
            for method in self.methods:
                if name != method.name:
                    continue
                for p1, p2 in zip(method.params, argTypes):
                    if not isCompatible(self.program, p1, p2):
                        continue
                return method
            return None

        res = self.methods.get(findMethod(), None)
        if not res and self.parent:
            return self.parent.lookupMethod(name, argTypes)
        return res

class MethodContext:
    def __init__(self, classContext):
        self.classContext = classContext
        self.formals = {}
        self.localVars = []
        self.loopDepth = 0
    def declareFormal(self, typename, name):
        self.formals[name] = typename
    def formalType(self, name):
        if name not in self.formals:
            return None
        return self.formals[name]
    def pushLoop(self):
        self.loopDepth += 1
    def popLoop(self):
        self.loopDepth -= 1
    @property
    def inloop(self):
        return self.loopDepth > 0

class LocalContext:
    '''
    Local Scope (nested)
    Class Definitions
    - Variables
    - Methods
    '''
    def __init__(self, method, parent=None):
        self.method = method
        self.parent = parent
        self.scope = {}
        self.constantScope = {}
    @property
    def program(self):
        return self.method.classContext.program
    @property
    def classContext(self):
        return self.method.classContext
    def varType(self, name):
        ''' Determines the type of name, regardless of whether name is
        a local variable, formal parameter, or class field'''
        res = self.scope.get(name, None)
        if not res:
            if self.parent:
                return self.parent.varType(name)
            else:
                res = self.method.formalType(name)
                if res:
                    return res
                return self.classContext.varType(name)
        return res
    def declareVar(self, typename, name):
        self.scope[name] = typename

    def declareConstVar(self, name, value):
        # used in optimizer for constant propogation \ folding
        self.constantScope[name] = value
    def getConstVar(self, name):
        value = self.constantScope.get(name, None)
        # used in optimizer for constant propogation \ folding
        if not value:
            if self.parent:
                return self.parent.getConstVar(name)
        return value

    def lookupClass(self, name):
        return self.classContext.program.lookupClass(name)
    def enterInnerScope(self):
        ''' Enter a new scope, using this scope as the parent '''
        return LocalContext(self.method, parent=self)

def isCompatible(program, src, dest):
    # if src is None, then return true
    if src.isObject() and dest.isObject():
        if dest.isNull():
            return False
        if src.isNull():
            return True

        src = program.lookupClass(src.name)
        dest = program.lookupClass(dest.name)

        while src:
            if src == dest:
                return True
            src = src.parent
        return False

    else:
        return src == dest

