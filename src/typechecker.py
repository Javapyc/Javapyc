
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
    stmts = self.children
    for stmt in stmts:
        stmt.typecheck(context)
    return 'Program'

@typechecks(ast.IntDecl)
def typecheck(self, context):
    (expr,) = self.children
    if expr.typecheck(context) != int:
        raise TypecheckException()
    #ensure not already declared
    if context.varType(self.name):
        raise TypecheckException()
    #record the declaration
    context.declareVar(self.typename, self.name)
    return ast.IntDecl

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



@typechecks(ast.Or)
@typechecks(ast.And)
def typecheck(self, context):
    left, right = self.children
    if left.typecheck(context) != bool or right.typecheck(context) != bool:
        raise TypecheckException()
    return bool

@typechecks(ast.BinaryEqualExpr)
def typecheck(self, context):
    left, right = self.children
    if left.typecheck(context) != right.typecheck(context):
        raise TypecheckException()
    return left.nodeType

@typechecks(ast.BinaryCompExpr)
def typecheck(self, context):
    left, right = self.children
    if left.typecheck(context) != int or right.typecheck(context) != int:
        raise TypecheckException()
    return bool

@typechecks(ast.Plus)
@typechecks(ast.Minus)
@typechecks(ast.Mult)
@typechecks(ast.Div)
def typecheck(self, context):
    left, right = self.children
    if left.typecheck(context) != int or right.typecheck(context) != int:
        raise TypecheckException()
    return left.nodeType

@typechecks(ast.Pow)
def typecheck(self, context):
    a, b = self.children
    if a.typecheck(context) != int or b.typecheck(context) != int:
        raise TypecheckException()
    return a.nodeType

@typechecks(ast.Negate)
def typecheck(self, context):
    if self.expr.typecheck(context) != int:
        raise TypecheckException()
    return self.expr.nodeType

@typechecks(ast.Not)
def typecheck(self, context):
    if self.expr.typecheck(context) != bool:
        raise TypecheckException()
    return self.expr.nodeType

@typechecks(ast.Boolean)
def typecheck(self, context):
    return bool

@typechecks(ast.Integer)
def typecheck(self, context):
    self.val = int(self.val)
    if self.val < ast.Integer.MIN_VALUE or self.val > ast.Integer.MAX_VALUE:
        raise TypecheckException()
    return int

@typechecks(ast.ID)
def typecheck(self, context):
    res = context.varType(self.name)
    if not res:
        raise TypecheckException()
    return res

def typecheck(tree):
    context = Context()
    tree.typecheck(context)

