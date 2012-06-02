
from copy import deepcopy
import ast
import settings

def debug(*args):
    if settings.shouldLog(2):
        print(*args)

def injectOptimization():
    def optimize(self):
        self.children = tuple(map(lambda child: child.optimize(), self.children))
        return self._optimize()
    setattr(ast.AST, 'optimize', optimize)

    def _optimize(self):
        return self
    setattr(ast.AST, '_optimize', _optimize)
injectOptimization()

def optimizes(cls):
    '''
    Annotates a function that will be added to the given class
    that returns an optimized version of itself, or itself if no
    optimization can be made
    '''
    def wrap(func):
        setattr(cls, '_optimize', func)
        return func
    return wrap

def preoptimizes(cls):
    '''
    Annotates a function that will be added to the given class
    that returns an optimized version of itself, or itself if no
    optimization can be made.  No prior optimizations are made to
    any children nodes.
    '''
    def wrap(func):
        setattr(cls, 'optimize', func)
        return func
    return wrap


def collapseBool(self, combine):
    left, right = self.children
    if isinstance(left, ast.Boolean) and isinstance(right, ast.Boolean):
        return ast.Boolean(combine(left.value(), right.value()))
    return self

def collapseComp(self, combine):
    left, right = self.children
    if isinstance(left, ast.Integer) and isinstance(right, ast.Integer):
        return ast.Boolean(combine(left.value(), right.value()))
    return self

def collapseInt(self, combine):
    left, right = self.children
    if isinstance(left, ast.Integer) and isinstance(right, ast.Integer):
        return ast.Integer(combine(left.value(), right.value()))
    return self

@optimizes(ast.ID)
def optimize(self):
    if self.context.program.optimizerInLoop > 0:
        return self

    if isinstance(self.context.varType(self.name), ast.BasicType):
        if self.context.varType(self.name)== ast.IntType:
            test = self.context.getConstVar(self.name)
            if test:
                return ast.Integer(test)
    return self

@optimizes(ast.Or)
def optimize(self):
    return collapseBool(self, lambda a,b: a or b)

@optimizes(ast.And)
def optimize(self):
    return collapseBool(self, lambda a,b: a and b)

@optimizes(ast.Equal)
def optimize(self):
    left, right = self.children
    if isinstance(left, ast.Integer) and isinstance(right, ast.Integer):
        return ast.Boolean(left.value() == right.value())
    elif isinstance(left, ast.Boolean) and isinstance(right, ast.Boolean):
        return ast.Boolean(left.value() == right.value())
    return self

@optimizes(ast.NotEqual)
def optimize(self):
    left, right = self.children
    if isinstance(left, ast.Integer) and isinstance(right, ast.Integer):
        return ast.Boolean(left.value() != right.value())
    elif isinstance(left, ast.Boolean) and isinstance(right, ast.Boolean):
        return ast.Boolean(left.value() != right.value())
    return self

@optimizes(ast.LessThan)
def optimize(self):
    return collapseComp(self, lambda a,b: a < b)

@optimizes(ast.GreaterThan)
def optimize(self):
    return collapseComp(self, lambda a,b: a > b)

@optimizes(ast.LessThanEqualTo)
def optimize(self):
    return collapseComp(self, lambda a,b: a <= b)

@optimizes(ast.GreaterThanEqualTo)
def optimize(self):
    return collapseComp(self, lambda a,b: a >= b)

@optimizes(ast.Plus)
def optimize(self):
    #TODO bound check
    return collapseInt(self, lambda a,b: a+b)

@optimizes(ast.Minus)
def optimize(self):
    #TODO bound check
    return collapseInt(self, lambda a,b: a-b)

@optimizes(ast.Mult)
def optimize(self):
    #TODO bound check
    return collapseInt(self, lambda a,b: a*b)

@optimizes(ast.Div)
def optimize(self):
    return collapseInt(self, lambda a,b: int(a/b))

@optimizes(ast.Pow)
def optimize(self):
    #TODO bound check
    return collapseInt(self, lambda a,b: int(a**b))

@optimizes(ast.Negate)
def optimize(self):
    (expr,) = self.children
    if isinstance(expr, ast.Integer):
        return ast.Integer(-expr.value())
    return self

@optimizes(ast.Not)
def optimize(self):
    (expr,) = self.children
    if isinstance(expr, ast.Boolean):
        return ast.Integer(not expr.value())
    return self

@preoptimizes(ast.If)
@preoptimizes(ast.IfElse)
def optimizeIfs(self):
    cond = self.children[0].optimize()

    self.context.program.optimizerInLoop += 1
    self.children = (cond,) + tuple(map(lambda child: child.optimize(), self.children[1:]))
    self.context.program.optimizerInLoop -= 1

    opt = self._optimize()
    return opt

@optimizes(ast.If)
def optimize(self):
    (cond, ifstmt) = self.children
    if isinstance(cond, ast.Boolean):
        if cond.val:
            return ifstmt.optimize()
        else:
            temp = ast.Nop()
            temp.context = self.context
            return temp
    return self

@optimizes(ast.IfElse)
def optimize(self):
    (cond, ifstmt, elsestmt) = self.children
    if isinstance(cond, ast.Boolean):
        if cond.val:
            return ifstmt
        else:
            return elsestmt
    return self

@preoptimizes(ast.While)
def optimize(self):
    self.context.program.optimizerInLoop += 1

    self.children = tuple(map(lambda child: child.optimize(), self.children))
    opt = self._optimize()

    self.context.program.optimizerInLoop -= 1 
    return opt

@optimizes(ast.While)
def optimize(self):
    (cond, stmt) = self.children
    if isinstance(cond, ast.Boolean) and not cond.val:
        temp = ast.Nop()
        temp.context = self.context
        return temp
    return self

@optimizes(ast.MethodDecl)
def optimize(self):
    *stmts, expr = self.children
    if len(stmts) == 0:
        formalTypes = tuple([i.typename for i in self.formallist])
        debug("\tMETHOD", self.ID, formalTypes, " can be inlined as (", expr, self.formallist, ")", self.context.classContext)
        debug()
        self.context.classContext.declareConstMethod(self.ID, formalTypes, self.formallist, expr)
    return self

def inlineSub(node, formalList, argList):
    if isinstance(node, ast.This):
        # can not optimize this calls
        return None


    if type(node) == ast.ID:
        if node.name in formalList:
            return argList[formalList.index(node.name)] 
        # reference to class static can not inline
        return None

    node.children = tuple(map(lambda x: inlineSub(x, formalList, argList), node.children))
    if None in node.children:
        return None

    return node

@optimizes(ast.Call)
def optimize(self):
    (var, *args) = self.children

    if isinstance(var, ast.ID):
        className = self.context.getConstVar(var.name)
        if not className:
            return self
    else:
        # can't optimize this.calls easily (too easy to mess up tail recursion)
        return self    

    classContext = self.context.lookupClass(className)

    formalTypes = tuple(map(lambda arg: arg.typecheck(self.context), args))

    temp = classContext.getConstMethod(self.func, formalTypes)
    if temp:
        (formallist, expr) = temp
        debug("call:", className, self.func, formalTypes, args, "\t=>", formallist, expr, expr.children, classContext)
        test = inlineSub(deepcopy(expr), [i.ID for i in formallist], args)

        if test:
            debug("hi:", test, test.children, "\t", expr, expr.children)
            debug()
            return test 

    return self

@optimizes(ast.Assignment)
def optimize(self):
    (expr,) = self.children
    if isinstance(expr, ast.Integer):
        self.context.declareConstVar(self.name, expr.val)
        debug("\t\tMapped", self.name, "=>", expr.val)
    else:
        self.context.declareConstVar(self.name, None)
        debug("\t\t", self.name, "no longer const", self.children, type(expr))
    return self    


@optimizes(ast.Decl)
def optimize(self):
    if isinstance(self.typename, ast.BasicType):
        if isinstance(self.children[0], ast.Integer):
            # have a named variable with a constant value (a = 10, b = 15)
            self.context.declareConstVar(self.name, self.children[0].val)
            debug("\t\tFound", self.name, "=>", self.children[0].val)

    if isinstance(self.typename, ast.ObjectType) and isinstance(self.children[0], ast.NewInstance):
        # have a named variable set to new XYZ()
        self.context.declareConstVar(self.name, self.children[0].name)
        debug("\t\tFound", self.name, "(new) =>", self.children[0].name)
    return self

@optimizes(ast.StmtList)
def optimize(self):
    (stmts) = self.children
    # Constant propogation (search for ID which are constant and pass constant instead of ID)

    newstmts = []
    for stmt in stmts:
        debug("\t-", stmt, stmt.children, self.context.program.optimizerInLoop)
        stmt = stmt.optimize()
        newstmts.append(stmt)

    self.children = newstmts
    return self

@preoptimizes(ast.StmtList)
def optimize(self):
    return self._optimize()

