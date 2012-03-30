
class AST:
    def __init__(self, children):
        self.children = children
    def classname(self):
        return self.__class__.__name__
    def __repr__(self):
        return "{0}".format(self.classname())

class Program(AST):
    def __init__(self, stmts):
        AST.__init__(self, stmts)

class Stmt(AST):
    pass
class Print(Stmt):
    def __init__(self, expr):
        AST.__init__(self, (expr,))

class Expr(AST):
    pass
class Or(Expr):
    def __init__(self, left, right):
        AST.__init__(self, (left,right))

class AndExpr(Expr):
    pass
class And(AndExpr):
    def __init__(self, left, right):
        AST.__init__(self, (left,right))

class EqualExpr(AndExpr):
    pass
class BinaryEqualExpr(EqualExpr):
    def __init__(self, left, right):
        AST.__init__(self, (left,right))
class Equal(BinaryEqualExpr):
    pass
class NotEqual(BinaryEqualExpr):
    pass

class CompExpr(EqualExpr):
    pass
class BinaryCompExpr(CompExpr):
    def __init__(self, left, right):
        AST.__init__(self, (left,right))
class LessThan(BinaryCompExpr):
    pass
class GreaterThan(BinaryCompExpr):
    pass
class LessThanEqualTo(BinaryCompExpr):
    pass
class GreaterThanEqualTo(BinaryCompExpr):
    pass

class AlgExpr(CompExpr):
    pass
class BinaryExpr(AlgExpr):
    def __init__(self, left, right):
        AST.__init__(self, (left,right))
        self.left = left
        self.right = right
class Plus(BinaryExpr):
    pass
class Minus(BinaryExpr):
    pass

class Term(AlgExpr):
    pass
class BinaryTerm(AlgExpr):
    def __init__(self, left, right):
        AST.__init__(self, (left,right))
        self.left = left
        self.right = right
class Mult(BinaryTerm):
    pass
class Div(BinaryTerm):
    pass

class Factor(Term):
    pass
class UnaryFactor(Factor):
    def __init__(self, expr):
        AST.__init__(self, (expr,))
        self.expr = expr
class Negate(UnaryFactor):
    pass
class Not(UnaryFactor):
    pass
class NewInstance(Factor):
    def __init__(self, name):
        AST.__init__(self, tuple())
        self.name = name
    def __repr__(self):
        return "New({0})".format(self.name)
class Scalar(Factor):
    def __repr__(self):
        return "({0}){1}".format(self.typename(), self.val)
class Integer(Scalar):
    def __init__(self, val):
        AST.__init__(self, tuple())
        self.val = val
    def typename(self):
        return 'int'
    def value(self):
        return int(self.val)
class Boolean(Scalar):
    def __init__(self, val):
        AST.__init__(self, tuple())
        self.val = val
    def typename(self):
        return 'bool'
    def value(self):
        return self.val
class Null(Factor):
    def __init__(self):
        AST.__init__(self, tuple())
    def __repr__(self):
        return 'null'
    def value(self):
        return None
class This(Factor):
    def __init__(self):
        AST.__init__(self, tuple())
    def __repr__(self):
        return 'this'
class ID(Factor):
    def __init__(self, name):
        AST.__init__(self, tuple())
        self.name = name
    def __repr__(self):
        return 'ID({0})'.format(self.name)
class Call(Factor):
    def __init__(self, obj, func, args):
        AST.__init__(self, (obj,) + tuple(args))
        self.obj = obj
        self.func = func
    def __repr__(self):
        return 'Call({0})'.format(self.func)

