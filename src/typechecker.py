
import ast

def typechecks(cls):
    def wrap(func):
        setattr(cls, '_typecheck', func)
        return func
    return wrap

class TypecheckException(Exception):
    pass

@typechecks(ast.Program)
def typecheck(self):
    stmts = self.children
    for stmt in stmts:
        stmt.typecheck()
    return 'Program'

@typechecks(ast.Print)
def typecheck(self):
    (expr,) = self.children
    expr.typecheck()
    return 'Stmt'

@typechecks(ast.Or)
@typechecks(ast.And)
def typecheck(self):
    left, right = self.children
    if left.typecheck() != bool or right.typecheck() != bool:
        raise TypecheckException()
    return bool

@typechecks(ast.BinaryEqualExpr)
def typecheck(self):
    left, right = self.children
    if left.typecheck() != right.typecheck():
        raise TypecheckException()
    return left.nodeType

@typechecks(ast.BinaryCompExpr)
def typecheck(self):
    left, right = self.children
    if left.typecheck() != int or right.typecheck() != int:
        raise TypecheckException()
    return bool

@typechecks(ast.Plus)
@typechecks(ast.Minus)
@typechecks(ast.Mult)
@typechecks(ast.Div)
def typecheck(self):
    left, right = self.children
    if left.typecheck() != int or right.typecheck() != int:
        raise TypecheckException()
    return left.nodeType

@typechecks(ast.Negate)
def typecheck(self):
    if self.expr.typecheck() != int:
        raise TypecheckException()
    return self.expr.nodeType

@typechecks(ast.Not)
def typecheck(self):
    if self.expr.typecheck() != bool:
        raise TypecheckException()
    return self.expr.nodeType

@typechecks(ast.Boolean)
def typecheck(self):
    return bool

@typechecks(ast.Integer)
def typecheck(self):
    #TODO check size of integer
    return int

def typecheck(tree):
    tree.typecheck()


