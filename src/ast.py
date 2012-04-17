
class AST:
    def __init__(self, children):
        self.children = children
        self.nodeType = None
    def classname(self):
        return self.__class__.__name__
    def __repr__(self):
        return "{0}".format(self.classname())

class Program(AST):
    def __init__(self, mainclass, classlist):
        AST.__init__(self, (mainclass,) + classlist)

class MainClassDecl(AST):
    def __init__(self, ID, argvName, stmts):
        AST.__init__(self, stmts)
        self.name = ID
        self.argvName = argvName
    def __repr__(self):
        return 'MainClass {0}'.format(self.name)

class ClassDecl(AST):
    def __init__(self, name, parent, classvars, methods):
        AST.__init__(self, tuple(methods))
        self.name = name
        self.parent = parent
        self.classvars = classvars
class BaseClassDecl(ClassDecl):
    def __repr__(self):
        return 'Class {0}'.format(self.name)
class DerivedClassDecl(ClassDecl):
    def __repr__(self):
        return 'Class {0} extends {1}'.format(self.name, self.parent)

class ClassVarDecl(AST):
    def __init__(self, typename, ID):
        AST.__init__(self, tuple())
        self.typename = typename
        self.ID = ID
    def __repr__(self):
        return "{0}({1}, {2})".format(self.classname(), self.typename, self.ID)

class MethodDecl(AST):
    def __init__(self, typename, ID, formallist, stmtlist, expr):
        AST.__init__(self, stmtlist + (expr,))
        self.typename = typename
        self.ID = ID
        self.formallist = formallist
    def __repr__(self):
        return "{0} {1}({2})".format(self.typename, self.ID, ', '.join(map(repr, self.formallist)))

class Formal(AST):
    def __init__(self, typename, ID):
        AST.__init__(self, tuple())
        self.typename = typename
        self.ID = ID
    def __repr__(self):
        return "{1} {2}".format(self.classname(), self.typename, self.ID)

class Type(AST):
    def __init__(self):
        AST.__init__(self, tuple())
    def isObject(self):
        return False
class BasicType(Type):
    def __init__(self, basicType):
        Type.__init__(self)
        self.basicType = basicType
    def __eq__(self, o):
        if not isinstance(o, BasicType):
            return False
        return self.basicType == o.basicType
    def __hash__(self):
        return hash(self.basicType)
    def __repr__(self):
        return "<{0}>".format(self.basicType.__name__)
IntType = BasicType(int)
BoolType = BasicType(bool)
class ObjectType(Type):
    def __init__(self, name):
        self.name = name
    def __eq__(self, o):
        if not isinstance(o, ObjectType):
            return False
        return self.name == o.name
    def __hash__(self):
        return hash(self.name)
    def __repr__(self):
        return self.name
    def isObject(self):
        return True

class Stmt(AST):
    pass
class MethodCall(Stmt):
    def __init__(self, expr):
        AST.__init__(self, (expr,))
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
class Assignment(Stmt):
    def __init__(self, name, expr):
        AST.__init__(self, (expr,))
        self.name = name
    def __repr__(self):
        return "{0}({1})".format(self.classname(), self.name)
class Print(Stmt):
    def __init__(self, expr):
        AST.__init__(self, (expr,))
class Printf(Stmt):
    def __init__(self, string, args):
        AST.__init__(self, tuple(args))
        self.string = string
        def escape(s):
            s = s.replace('\n', '\\n')
            s = s.replace('\\', '\\\\')
            s = s.replace('\"', '\"')
            return s
        self.displaystring = escape(string)
    def __repr__(self):
        return "{0}({1})".format(self.classname(), str(self.displaystring))
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

