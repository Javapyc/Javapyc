
class AST:
    def __init__(self, children):
        self.children = children
    def classname(self):
        return self.__class__.__name__
    def __repr__(self):
        return "{0}".format(self.classname())
    def typecheck(self):
        self.nodeType = self._typecheck()
        return self.nodeType

class Program(AST):
    def __init__(self, stmts):
        AST.__init__(self, stmts)
    def codegen(self, c):
        stmts = self.children
        for stmt in stmts:
            stmt.codegen(c)

class Stmt(AST):
    pass
class Print(Stmt):
    def __init__(self, expr):
        AST.__init__(self, (expr,))
    def codegen(self, c):
        (expr,) = self.children
        c.LOAD_NAME('print')
        expr.codegen(c)
        c.CALL_FUNCTION(1)
        c.POP_TOP()

class Expr(AST):
    pass
class Or(Expr):
    def __init__(self, left, right):
        AST.__init__(self, (left,right))
    def value(self):
        left, right = self.children
        return left.value() or right.value()

class AndExpr(Expr):
    pass
class And(AndExpr):
    def __init__(self, left, right):
        AST.__init__(self, (left,right))
    def value(self):
        left, right = self.children
        return left.value() and right.value()

class EqualExpr(AndExpr):
    pass
class BinaryEqualExpr(EqualExpr):
    def __init__(self, left, right):
        AST.__init__(self, (left,right))
class Equal(BinaryEqualExpr):
    def value(self):
        left, right = self.children
        return left.value() == right.value()
class NotEqual(BinaryEqualExpr):
    def value(self):
        left, right = self.children
        return left.value() != right.value()

class CompExpr(EqualExpr):
    pass
class BinaryCompExpr(CompExpr):
    def __init__(self, left, right):
        AST.__init__(self, (left,right))
class LessThan(BinaryCompExpr):
    def value(self):
        left, right = self.children
        return left.value() < right.value()
class GreaterThan(BinaryCompExpr):
    def value(self):
        left, right = self.children
        return left.value() > right.value()
class LessThanEqualTo(BinaryCompExpr):
    def value(self):
        left, right = self.children
        return left.value() <= right.value()
class GreaterThanEqualTo(BinaryCompExpr):
    def value(self):
        left, right = self.children
        return left.value() >= right.value()

class AlgExpr(CompExpr):
    pass
class BinaryExpr(AlgExpr):
    def __init__(self, left, right):
        AST.__init__(self, (left,right))
        self.left = left
        self.right = right
class Plus(BinaryExpr):
    def value(self):
        return self.left.value() + self.right.value()
    def codegen(self, c):
        self.left.codegen(c)
        self.right.codegen(c)
        c.BINARY_ADD()
class Minus(BinaryExpr):
    def value(self):
        return self.left.value() - self.right.value()
    def codegen(self, c):
        self.left.codegen(c)
        self.right.codegen(c)
        c.BINARY_SUBTRACT()

class Term(AlgExpr):
    pass
class BinaryTerm(AlgExpr):
    def __init__(self, left, right):
        AST.__init__(self, (left,right))
        self.left = left
        self.right = right
class Mult(BinaryTerm):
    def value(self):
        return self.left.value() * self.right.value()
    def codegen(self, c):
        self.left.codegen(c)
        self.right.codegen(c)
        c.BINARY_MULTIPLY()
class Div(BinaryTerm):
    def value(self):
        return int(self.left.value() / self.right.value())
    def codegen(self, c):
        self.left.codegen(c)
        self.right.codegen(c)
        c.BINARY_FLOOR_DIVIDE()

class Factor(Term):
    pass
class UnaryFactor(Factor):
    def __init__(self, expr):
        AST.__init__(self, (expr,))
        self.expr = expr
class Negate(UnaryFactor):
    def value(self):
        return -self.expr.value()
class Not(UnaryFactor):
    def value(self):
        return not self.expr.value()
class NewInstance(Factor):
    def __init__(self, name):
        AST.__init__(self, tuple())
        self.name = name
    def __repr__(self):
        return "New({0})".format(self.name)
    def value(self):
        return None
class Scalar(Factor):
    def __repr__(self):
        return "({0}){1}".format(self.typename(), self.val)
class Integer(Scalar):
    def __init__(self, val):
        AST.__init__(self, tuple())
        self.val = val.val
    def typename(self):
        return 'int'
    def value(self):
        return int(self.val)
    def codegen(self, c):
        c.LOAD_CONST(self.val)
class Boolean(Scalar):
    def __init__(self, val):
        AST.__init__(self, tuple())
        self.val = val
    def typename(self):
        return 'bool'
    def value(self):
        return self.val
    def codegen(self, c):
        c.LOAD_CONST(self.val)
class Null(Factor):
    def __init__(self):
        AST.__init__(self, tuple())
    def __repr__(self):
        return 'null'
    def value(self):
        return None
    def codegen(self, c):
        c.LOAD_CONST(None)
class This(Factor):
    def __init__(self):
        AST.__init__(self, tuple())
    def __repr__(self):
        return 'this'
    def value(self):
        return None
class ID(Factor):
    def __init__(self, name):
        AST.__init__(self, tuple())
        self.name = name
    def __repr__(self):
        return 'ID({0})'.format(self.name)
    def value(self):
        return None
class Call(Factor):
    def __init__(self, obj, func, args):
        AST.__init__(self, (obj,) + tuple(args))
        self.obj = obj
        self.func = func
    def __repr__(self):
        return 'Call({0})'.format(self.func)
    def value(self):
        return None

