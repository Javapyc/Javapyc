
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
    def __init__(self, name, variables, methods, parent=None):
        self.name = name
        self.variables = variables
        self.methods = methods
        self.parent = parent
        self.program = None
    def varType(self, name):
        return self.variables.get(name, None)
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
    def declareFormal(self, typename, name):
        self.formals[name] = typename
    def formalType(self, name):
        if name not in self.formals:
            return None
        return self.formals[name]

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
    def lookupClass(self, name):
        return self.classContext.program.lookupClass(name)
    def enterInnerScope(self):
        ''' Enter a new scope, using this scope as the parent '''
        return LocalContext(self.method, parent=self)

@typechecks(ast.Program)
def typecheck(self, context):
    mainclass, *classes = self.children

    self.context = context
    for cls in classes:
        methods = cls.children
        
        varMap = {}
        for var in cls.classvars:
            if var.ID in varMap:
                raise TypecheckException("Duplicate definition of field: {0}".format(var.ID))
            varMap[var.ID] = var.typename

        methodMap = {}
        for method in methods:
            method.types = tuple(map(lambda formal: formal.typename, method.formallist))
            methodMap[MethodPrototype(method.ID, method.types)] = method.typename

        parentClass = None
        if cls.parent:
            parentClass = context.lookupClass(cls.parent)
            if not parentClass:
                raise TypecheckException("'{0}' does not have a parent".format(cls))
        
        classContext = ClassContext(cls.name, varMap, methodMap, parent=parentClass)
        context.registerClass(cls.name, classContext)

    mainClassContext = ClassContext(mainclass.name, dict(), dict())
    context.registerClass(mainclass.name, mainClassContext)
    mainclass.typecheck(mainClassContext)

    for classType in classes:
        classType.typecheck(context.lookupClass(classType.name))
    return ast.Program

@typechecks(ast.MainClassDecl)
def typecheck(self, context):
    stmts = self.children
    methodContext = MethodContext(context)
    methodContext.declareFormal('String[]', self.argvName)
    self.context = methodContext

    localContext = LocalContext(methodContext) 
    for stmt in stmts:
        stmt.typecheck(localContext)

    return ast.MainClassDecl

@typechecks(ast.ClassDecl)
def typecheck(self, context):
    methods = self.children

    for method in methods:
        method.typecheck(context)

    return type(self)

@typechecks(ast.MethodDecl)
def typecheck(self, context):
    *stmts, expr = self.children
    methodContext = MethodContext(context)
    self.context = methodContext

    for formal in self.formallist:
        methodContext.declareFormal(formal.typename, formal.ID)

    localContext = LocalContext(methodContext)
    for stmt in stmts:
        stmt.typecheck(localContext)

    retType = context.lookupMethod(self.ID, self.types)
    if expr.typecheck(localContext) != retType:
        raise TypecheckException("Invalid return type")

    return ast.MethodDecl

@typechecks(ast.Type)
def typecheck(self, context):
    raise TypecheckException("Can't typecheck a type")

@typechecks(ast.MethodCall)
def typecheck(self, context):
    (call,) = self.children

    call.typecheck(context)

    return ast.MethodCall

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
        raise TypecheckException("Cannot assign {0} to {1}".format(expr, self.typename))
    #ensure not already declared
    if context.varType(self.name):
        raise TypecheckException("Illegal redeclaration of variable '{0}'".format(self.name))
    #record the declaration
    context.declareVar(self.typename, self.name)
    return ast.Decl

@typechecks(ast.Assignment)
def typecheck(self, context):
    (expr,) = self.children
    varType = context.varType(self.name)
    if not isCompatible(context.program, expr.typecheck(context), varType):
        raise TypecheckException("Cannot assign {0} to {1}".format(expr, varType))
    return expr.nodeType

@typechecks(ast.Print)
def typecheck(self, context):
    (expr,) = self.children
    if expr.typecheck(context) != ast.IntType:
        raise TypecheckException("Error with println: can only print Integers (I know, I know...)")
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
                raise TypecheckException("Error with printf: format type does not match argument")
    argTypes = list(types(self.string))

    if len(argTypes) != len(args):
        raise TypecheckException()

    for arg, t in zip(args, argTypes):
        if arg.nodeType != t:
            raise TypecheckException("Printf problem")

    self.string = self.string.replace('%b', '%s')

    return ast.Printf

@typechecks(ast.If)
def typecheck(self, context):
    cond, ifstmt, elsestmt = self.children
    
    if cond.typecheck(context) != ast.BoolType:
        raise TypecheckException("Error with If: condition must be boolean")

    if ifstmt.typecheck(context) == ast.Decl:
        raise TypecheckException("Error with If: cannot have single declaration in if")

    if elsestmt.typecheck(context) == ast.Decl:
        raise TypecheckException("Error with If: cannot have single declaration in else block")

    return ast.If

@typechecks(ast.While)
def typecheck(self, context):
    cond, stmt = self.children
    
    if cond.typecheck(context) != ast.BoolType:
        raise TypecheckException("Error with While: condition must be boolean")

    if stmt.typecheck(context) == ast.Decl:
        raise TypecheckException("Error with While: cannot have single declaration in while")

    return ast.While

    
@typechecks(ast.Or)
@typechecks(ast.And)
def typecheck(self, context):
    left, right = self.children
    if left.typecheck(context) != ast.BoolType:
        raise TypecheckException("Left side of && must be boolean, is {0}".format(left))
    if right.typecheck(context) != ast.BoolType:
        raise TypecheckException("Right side of && must be boolean, is {0}".format(right))
    
    return ast.BoolType

@typechecks(ast.BinaryEqualExpr)
def typecheck(self, context):
    left, right = self.children
    if left.typecheck(context) != right.typecheck(context):
        raise TypecheckException("Types of left and right sides of == must agree")
    return ast.BoolType

@typechecks(ast.BinaryCompExpr)
def typecheck(self, context):
    left, right = self.children
    if left.typecheck(context) != ast.IntType:
        raise TypecheckException("Left side of comparison must be int, is {0}".format(left))
    if right.typecheck(context) != ast.IntType:
        raise TypecheckException("Right side of comparison must be int, is {0}".format(right))
    return ast.BoolType

@typechecks(ast.Plus)
@typechecks(ast.Minus)
@typechecks(ast.Mult)
@typechecks(ast.Div)
def typecheck(self, context):
    left, right = self.children
    if left.typecheck(context) != ast.IntType:
        raise TypecheckException("Left side of / must be int, is {0}".format(left))
    if right.typecheck(context) != ast.IntType:
        raise TypecheckException("Right side of / must be int, is {0}".format(right))
    return left.nodeType

@typechecks(ast.Negate)
def typecheck(self, context):
    if self.expr.typecheck(context) != ast.IntType:
        raise TypecheckException("Cannot negate a non-integer: {0}".format(self.expr))
    return self.expr.nodeType

@typechecks(ast.Not)
def typecheck(self, context):
    if self.expr.typecheck(context) != ast.BoolType:
        raise TypecheckException("Cannot take logical Not of non-boolean: {0}".format(self.expr))
    return self.expr.nodeType

@typechecks(ast.NewInstance)
def typecheck(self, context):
    newClass = context.lookupClass(self.name)

    if not newClass:
        raise TypecheckException("Cannot create new instance of undeclared class '{0}'".format(self.name))

    return ast.ObjectType(self.name)

@typechecks(ast.Boolean)
def typecheck(self, context):
    return ast.BoolType

@typechecks(ast.Integer)
def typecheck(self, context):
    self.val = int(self.val)
    if self.val < ast.Integer.MIN_VALUE or self.val > ast.Integer.MAX_VALUE:
        raise TypecheckException("Integer {0} is out of bounds".format(self.val))
    return ast.IntType

@typechecks(ast.Null)
def typecheck(self, context):
    return ast.NullType

@typechecks(ast.This)
def typecheck(self, context):
    return ast.ObjectType(context.classContext.name)

@typechecks(ast.ID)
def typecheck(self, context):
    res = context.varType(self.name)
    if not res:
        raise TypecheckException("Variable {0} has not been declared".format(self.name))
    return res

@typechecks(ast.Pow)
def typecheck(self, context):
    a, b = self.children
    if a.typecheck(context) != ast.IntType or b.typecheck(context) != ast.IntType:
        raise TypecheckException("Arguments to Math.pow must be integers, are {0}, {1}".format(a, b))
    return a.nodeType

@typechecks(ast.Call)
def typecheck(self, context):
    (obj, *args) = self.children

    objType = obj.typecheck(context)
    argTypes = tuple(map(lambda arg: arg.typecheck(context), args))

    if not objType.isObject() or objType.isNull():
        raise TypecheckException("Cannot call methods from non-object '{0}'".format(objType))

    classContext = context.lookupClass(objType.name)

    #Ensure class exists
    if not classContext:
        raise TypecheckException("Class {0} does not exist".format(objType))

    retType = classContext.lookupMethod(self.func, argTypes)

    if not retType:
        raise TypecheckException("Method not found: {0}({1})".format(
            self.func, ', '.join(map(str,argTypes))))

    return retType

def typecheck(tree):
    context = ProgramContext()
    tree.typecheck(context)

