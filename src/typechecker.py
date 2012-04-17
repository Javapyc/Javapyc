
import ast

def injectTypecheck():
    def typecheck(self, *args):
        self.nodeType = self._typecheck(*args)
        return self.nodeType
    setattr(ast.AST, 'typecheck', typecheck)
injectTypecheck()

def typechecks(cls):
    def wrap(func):
        setattr(cls, '_typecheck', func)
        return func
    return wrap

class TypecheckException(Exception):
    pass

class MethodPrototype:
    def __init__(self, name, params):
        self.name = name
        self.params = params
    def __eq__(self, o):
        return self.name == o.name and o.params == o.params
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
    def __init__(self, name, variables, methods, parent=None):
        self.name = name
        self.variables = variables
        self.methods = methods
        self.parent = parent
        self.program = None
    def lookupMethod(self, name, argTypes):
        res = self.methods.get(MethodPrototype(name, argTypes), None)
        if not res and self.parent:
            return self.parent.lookupMethod(name, argTypes)
        return res

class LocalContext:
    '''
    Local Scope (nested)
    Class Definitions
    - Variables
    - Methods
    '''
    def __init__(self, classContext, parent=None):
        self.scope = {}
        self.classContext = classContext
        self.parent = parent
    @property
    def program(self):
        return self.classContext.program
    def varType(self, name):
        res = self.scope.get(name, None)
        if not res and self.parent:
            return self.parent.varType(name)
        return res
    def declareVar(self, typename, name):
        self.scope[name] = typename
    def lookupClass(self, name):
        return self.classContext.program.lookupClass(name)
    def enterInnerScope(self):
        ''' Enter a new scope, using this scope as the parent '''
        return LocalContext(self.classContext, parent=self)

@typechecks(ast.Program)
def typecheck(self, context):
    mainclass, *classes = self.children

    for cls in classes:
        methods = cls.children
        
        varMap = {}
        for var in cls.classvars:
            varMap[var.ID] = var.typename

        methodMap = {}
        for method in methods:
            types = tuple(map(lambda formal: formal.typename, method.formallist))
            methodMap[MethodPrototype(method.ID, types)] = method.typename

        parentClass = None
        if cls.parent:
            parentClass = context.lookupClass(cls.parent)
            if not parentClass:
                raise TypecheckException()
        
        classContext = ClassContext(cls.name, varMap, methodMap, parent=parentClass)
        context.registerClass(cls.name, classContext)

    mainClassContext = ClassContext(mainclass.name, tuple(), tuple())
    context.registerClass(mainclass.name, mainClassContext)
    mainclass.typecheck(mainClassContext)

    #TODO classes
    #for classType in classes:
    #    classType.typecheck(context)
    return ast.Program

@typechecks(ast.MainClassDecl)
def typecheck(self, context):
    stmts = self.children
    local = LocalContext(context)
    local.declareVar('String[]', self.argvName)
    
    for stmt in stmts:
        stmt.typecheck(local)

    return ast.MainClassDecl

#TODO ClassDecl

#TODO ClassVarDecl
#TODO MethodDecl
#TODO Formal
#TODO Type

#TODO MethodCall

def isCompatible(program, src, dest):
    if src.isObject() and dest.isObject():
        src = program.lookupClass(src.name)
        dest = program.lookupClass(dest.name)

        while src:
            if src == dest:
                return True
            src = src.parent
        return False

    else:
        return src == dest

@typechecks(ast.StmtList)
def typecheck(self, context):
    stmts = self.children
    context = context.enterInnerScope()

    for stmt in stmts:
        stmt.typecheck(context)

@typechecks(ast.Decl)
def typecheck(self, context):
    (expr,) = self.children
    if not isCompatible(context.program, expr.typecheck(context), self.typename):
        raise TypecheckException()
    #ensure not already declared
    if context.varType(self.name):
        raise TypecheckException()
    #record the declaration
    context.declareVar(self.typename, self.name)
    return ast.Decl

@typechecks(ast.Assignment)
def typecheck(self, context):
    (expr,) = self.children
    varType = context.varType(self.name)
    if not isCompatible(context.program, expr.typecheck(context), varType):
        raise TypecheckException()
    return expr.nodeType

@typechecks(ast.Print)
def typecheck(self, context):
    (expr,) = self.children
    if expr.typecheck(context) != ast.IntType:
        raise TypecheckException()
    return ast.Print

@typechecks(ast.Printf)
def typecheck(self, context):
    args = self.children
    for arg in args:
        arg.typecheck(context)

    def types(s):
        ls = s.split("%")
        if len(ls) == 1:
            return
        for sub in ls[1:]:
            if len(sub) == 0:
                raise TypecheckException()
            c = sub[0]
            if c == 'd':
                yield ast.IntType
            elif c == 'b':
                yield ast.BoolType
            else:
                raise TypecheckException()
    argTypes = list(types(self.string))

    if len(argTypes) != len(args):
        raise TypecheckException()

    for arg, t in zip(args, argTypes):
        if arg.nodeType != t:
            raise TypecheckException()

    self.string = self.string.replace('%b', '%s')

    return ast.Printf

@typechecks(ast.If)
def typecheck(self, context):
    cond, ifstmt, elsestmt = self.children
    
    if cond.typecheck(context) != ast.BoolType:
        raise TypecheckException()

    if ifstmt.typecheck(context) == ast.Decl:
        raise TypecheckException()

    if elsestmt.typecheck(context) == ast.Decl:
        raise TypecheckException()

    return ast.If

#TODO While

@typechecks(ast.Or)
@typechecks(ast.And)
def typecheck(self, context):
    left, right = self.children
    if left.typecheck(context) != ast.BoolType or right.typecheck(context) != ast.BoolType:
        raise TypecheckException()
    return ast.BoolType

@typechecks(ast.BinaryEqualExpr)
def typecheck(self, context):
    left, right = self.children
    if left.typecheck(context) != right.typecheck(context):
        raise TypecheckException()
    return ast.BoolType

@typechecks(ast.BinaryCompExpr)
def typecheck(self, context):
    left, right = self.children
    if left.typecheck(context) != ast.IntType or right.typecheck(context) != ast.IntType:
        raise TypecheckException()
    return ast.BoolType

@typechecks(ast.Plus)
@typechecks(ast.Minus)
@typechecks(ast.Mult)
@typechecks(ast.Div)
def typecheck(self, context):
    left, right = self.children
    if left.typecheck(context) != ast.IntType or right.typecheck(context) != ast.IntType:
        raise TypecheckException()
    return left.nodeType

@typechecks(ast.Negate)
def typecheck(self, context):
    if self.expr.typecheck(context) != ast.IntType:
        raise TypecheckException()
    return self.expr.nodeType

@typechecks(ast.Not)
def typecheck(self, context):
    if self.expr.typecheck(context) != ast.BoolType:
        raise TypecheckException()
    return self.expr.nodeType

@typechecks(ast.NewInstance)
def typecheck(self, context):
    newClass = context.lookupClass(self.name)

    if not newClass:
        raise TypecheckException()

    return ast.ObjectType(self.name)

@typechecks(ast.Boolean)
def typecheck(self, context):
    return ast.BoolType

@typechecks(ast.Integer)
def typecheck(self, context):
    self.val = int(self.val)
    if self.val < ast.Integer.MIN_VALUE or self.val > ast.Integer.MAX_VALUE:
        raise TypecheckException()
    return ast.IntType

@typechecks(ast.Null)
def typecheck(self, context):
    return type(None)

@typechecks(ast.This)
def typecheck(self, context):
    return ObjectType(self.classContext.name)

@typechecks(ast.ID)
def typecheck(self, context):
    res = context.varType(self.name)
    if not res:
        raise TypecheckException()
    return res

@typechecks(ast.Pow)
def typecheck(self, context):
    a, b = self.children
    if a.typecheck(context) != ast.IntType or b.typecheck(context) != ast.IntType:
        raise TypecheckException()
    return a.nodeType

@typechecks(ast.Call)
def typecheck(self, context):
    (obj, *args) = self.children

    objType = obj.typecheck(context)
    argTypes = tuple(map(lambda arg: arg.typecheck(context), args))

    if not objType.isObject():
        raise TypecheckException()

    classContext = context.lookupClass(objType.name)

    if not classContext:
        raise TypecheckException()

    retType = classContext.lookupMethod(self.func, argTypes)
    
    if not retType:
        raise TypecheckException()

    return retType

def typecheck(tree):
    context = ProgramContext()
    tree.typecheck(context)

