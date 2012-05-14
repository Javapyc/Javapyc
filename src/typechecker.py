
import ast
import settings
from context import *

def injectTypecheck():
    def typecheck(self, context):
        self.context = context
        self.nodeType = self._typecheck(context)
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

@typechecks(ast.Program)
def typecheck(self, context):
    mainclass, *classes = self.children

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
            for prototype in methodMap:
                if method.ID == prototype.name:
                    raise TypecheckException("Duplicate definition of method: {0}".format(method.ID))
            key = MethodPrototype(method.ID, method.types)
            methodMap[key] = method.typename

        parentClass = None
        if cls.parent:
            parentClass = context.lookupClass(cls.parent)
            if not parentClass:
                raise TypecheckException("'{0}' does not have a parent".format(cls))
        
        classContext = ClassContext(cls.name, cls.classvars, varMap, methodMap, parent=parentClass)
        context.registerClass(cls.name, classContext)

    mainClassContext = ClassContext(mainclass.name, list(), dict(), dict())
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
    methodContext.retType = context.lookupMethod(self.ID, self.types)

    localContext = LocalContext(methodContext)
    for stmt in stmts:
        stmt.typecheck(localContext)

    if self.isMethod():
        if not isCompatible(localContext.program, expr.typecheck(localContext), methodContext.retType):
            raise TypecheckException("Invalid return type")

        if self.ID == 'toString' and (methodContext.retType != ast.StringType or len(self.formallist) != 0):
            raise TypecheckException("toString must return String and accept 0 parameters")
    elif self.isGenerator():
        pass
    else:
        raise TypecheckException("Return statement required if not a generator") 

    return ast.MethodDecl

@typechecks(ast.Type)
def typecheck(self, context):
    raise TypecheckException("Can't typecheck a type")

@typechecks(ast.MethodCall)
def typecheck(self, context):
    settings.requireExtended();

    (call,) = self.children

    call.typecheck(context)

    return ast.MethodCall

@typechecks(ast.StmtList)
def typecheck(self, context):
    stmts = self.children
    context = context.enterInnerScope()
    self.context = context

    for stmt in stmts:
        stmt.typecheck(context)

@typechecks(ast.Decl)
def typecheck(self, context):
    (expr,) = self.children
    if not isCompatible(context.program, expr.typecheck(context), self.typename):
        raise TypecheckException("Cannot assign {0} to {1}".format(expr, self.typename))
    #ensure not already declared
    if context.localVarType(self.name):
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
    settings.requireExtended();

    (formatString,) = self.children
    formatString.typecheck(context)

    return ast.Printf

@typechecks(ast.Yield)
def typecheck(self, context):
    settings.requireExtended();

    (expr,) = self.children
    
    if not isCompatible(context.program, expr.typecheck(context), context.method.retType):
        raise TypecheckException("Invalid yield type")

    return ast.Yield

@typechecks(ast.If)
def typecheck(self, context):
    settings.requireExtended();
    
    cond, ifstmt = self.children
    
    if cond.typecheck(context) != ast.BoolType:
        raise TypecheckException("Error with If: condition must be boolean")

    if ifstmt.typecheck(context) == ast.Decl:
        raise TypecheckException("Error with If: cannot have single declaration in if")

    return ast.If

@typechecks(ast.IfElse)
def typecheck(self, context):
    cond, ifstmt, elsestmt = self.children
    
    if cond.typecheck(context) != ast.BoolType:
        raise TypecheckException("Error with If: condition must be boolean")

    if ifstmt.typecheck(context) == ast.Decl:
        raise TypecheckException("Error with If: cannot have single declaration in if")

    if elsestmt.typecheck(context) == ast.Decl:
        raise TypecheckException("Error with If: cannot have single declaration in else block")

    return ast.IfElse

@typechecks(ast.While)
def typecheck(self, context):
    cond, stmt = self.children
    
    context.method.pushLoop()
    if cond.typecheck(context) != ast.BoolType:
        raise TypecheckException("Error with While: condition must be boolean")

    if stmt.typecheck(context) == ast.Decl:
        raise TypecheckException("Error with While: cannot have single declaration in while")
    context.method.popLoop()

    return ast.While

@typechecks(ast.ForEach)
def typecheck(self, context):
    expr, stmt = self.children
    
    context = context.enterInnerScope()
    self.context = context
    context.method.pushLoop()

    if not isCompatible(context.program, expr.typecheck(context), self.typename):
        raise TypecheckException("Cannot assign {0} to {1}".format(expr, self.typename))
    #ensure not already declared
    if context.localVarType(self.name):
        raise TypecheckException("Illegal redeclaration of variable '{0}'".format(self.name))
    context.declareVar(self.typename, self.name)

    if stmt.typecheck(context) == ast.Decl:
        raise TypecheckException("Error with ForEach: cannot have single declaration in loop")
    context.method.popLoop()

    return ast.ForEach

@typechecks(ast.Break)
def typecheck(self, context):
    settings.requireExtended();
    if not context.method.inloop:
        raise TypecheckException("Break outside of loop")
    
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
    leftType = left.typecheck(context)
    rightType = right.typecheck(context)
    if (not isCompatible(context.program, leftType, rightType) and
        not isCompatible(context.program, rightType, leftType)):
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

@typechecks(ast.String)
def typecheck(self, context):
    return ast.StringType

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
    settings.requireExtended();

    a, b = self.children
    if a.typecheck(context) != ast.IntType or b.typecheck(context) != ast.IntType:
        raise TypecheckException("Arguments to Math.pow must be integers, are {0}, {1}".format(a, b))
    return a.nodeType

@typechecks(ast.StringFormat)
def typecheck(self, context):
    settings.requireExtended();

    (formatString,) = self.children
    formatString.typecheck(context)

    return ast.StringType

@typechecks(ast.FormatString)
def typecheck(self, context):
    settings.requireExtended();

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
                yield (ast.IntType, )
            elif c == 'b':
                yield (ast.BoolType, )
            elif c == 's':
                yield (ast.StringType, ast.BaseObjectType)
            else:
                raise TypecheckException("Format string: unknown format type")
    argTypes = list(types(self.string))

    if len(argTypes) != len(args):
        raise TypecheckException()

    for arg, t in zip(args, argTypes):
        if (arg.nodeType not in t) and not (ast.BaseObjectType in t and isinstance(arg.nodeType, ast.BaseObjectType)):
            raise TypecheckException("Format string: format type does not match argument")

    self.string = self.string.replace('%b', '%s')

    return ast.FormatString

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

