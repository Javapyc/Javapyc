
class AST:
    def __init__(self, children):
        self.children = children
        self.nodeType = None
    def classname(self):
        return self.__class__.__name__
    def __repr__(self):
        return "{0}".format(self.classname())

class Program(AST):
    def __init__(self, stmts):
        AST.__init__(self, stmts)

class IDList(AST):
    def __init__(self, left, right):
        AST.__init__(self, (left, right))

class IntegerList(AST):
    def __init__(self, left, right):
        AST.__init__(self, (left, right))

class Type(AST):
    def __init__(self, typename):
        AST.__init__(self, tuple())
        self.typename = typename
    def __repr__(self):
        return "{0}({1})".format(self.classname(), self.typename)

class Stmt(AST):
    pass
class StmtList(Stmt):
    def __init__(self, stmts):
        AST.__init__(self, stmts)
class Decl(Stmt):
    def __init__(self, typename, name, expr):
        AST.__init__(self, (expr,))
        self.typename = typename
        self.name = name
    def __repr__(self):
        return "{0}({1}, {2})".format(self.classname(), self.typename, self.name)
class IntDecl(Decl):
    def __init__(self, name, expr):
        Decl.__init__(self, int, name, expr)
class BoolDecl(Decl):
    def __init__(self, name, expr):
        Decl.__init__(self, bool, name, expr)
class TypeDecl(Decl):
    def __init__(self, typename, name, expr):
        Decl.__init__(self, typename, name, expr)
class Assignment(Stmt):
    def __init__(self, name, expr):
        AST.__init__(self, (expr,))
        self.name = name
    def __repr__(self):
        return "{0}({1})".format(self.classname(), self.name)
class Print(Stmt):
    def __init__(self, expr):
        AST.__init__(self, (expr,))
class If(Stmt):
    def __init__(self, cond, ifstmt, elsestmt):
        AST.__init__(self, (cond, ifstmt, elsestmt))
class While(Stmt):
    def __init__(self, cond, stmt):
        AST.__init__(self, (cond, stmt))


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
    MIN_VALUE = -0x80000000
    MAX_VALUE = 0x80000000-1
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
class Pow(Factor):
    def __init__(self, a, b):
        AST.__init__(self, (a,b))
    def __repr__(self):
        return 'Pow'
class Call(Factor):
    def __init__(self, obj, func, args):
        AST.__init__(self, (obj,) + tuple(args))
        self.obj = obj
        self.func = func
    def __repr__(self):
        return 'Call({0})'.format(self.func)

