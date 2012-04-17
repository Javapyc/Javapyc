
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

class Context:
    def __init__(self, parent=None):
        self.parent = parent
        self.scope = {}
    def varType(self, name):
        res = self.scope.get(name, None)
        if not res and self.parent:
            return self.parent.varType(name)
        return res
    def declareVar(self, typename, name):
        self.scope[name] = typename
    def inner(self):
        ''' Enter a new scope, using this scope as the parent '''
        return Context(self)

@typechecks(ast.Program)
def typecheck(self, context):
    mainclass, *classes = self.children
    mainclass.typecheck(context)
    #for classType in classes:
    #    classType.typecheck(context)
    return 'Program'

@typechecks(ast.MainClassDecl)
def typecheck(self, context):
    stmts = self.children
    #TODO add argvName to context
    #TODO register main class name
    for stmt in stmts:
        stmt.typecheck(context)

    return 'MainClassDecl'

@typechecks(ast.Decl)
def typecheck(self, context):
    #TODO handle bool and custom types
    (expr,) = self.children
    if expr.typecheck(context) != self.typename:
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
    if expr.typecheck(context) != context.varType(self.name):
        raise TypecheckException()
    return expr.nodeType

@typechecks(ast.Print)
def typecheck(self, context):
    (expr,) = self.children
    expr.typecheck(context)
    return 'Stmt'

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

    return 'Stmt'

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
    return left.nodeType

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

@typechecks(ast.Pow)
def typecheck(self, context):
    a, b = self.children
    if a.typecheck(context) != ast.IntType or b.typecheck(context) != ast.IntType:
        raise TypecheckException()
    return a.nodeType

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

@typechecks(ast.Boolean)
def typecheck(self, context):
    return ast.BoolType

@typechecks(ast.Integer)
def typecheck(self, context):
    self.val = int(self.val)
    if self.val < ast.Integer.MIN_VALUE or self.val > ast.Integer.MAX_VALUE:
        raise TypecheckException()
    return ast.IntType

@typechecks(ast.ID)
def typecheck(self, context):
    res = context.varType(self.name)
    if not res:
        raise TypecheckException()
    return res

def typecheck(tree):
    context = Context()
    tree.typecheck(context)

