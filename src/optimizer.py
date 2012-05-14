import ast

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


def collapseConstantInt(self):
    left, right = self.children

    if isinstance(left, ast.Integer) and isinstance(right, ast.Integer):
        return ast.Integer(left.val + right.val)
    return self

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
        # FIXME TODO this feels wrong with "== int"
        if self.context.varType(self.name).basicType == int:
            test = self.context.getConstVar(self.name)
            if test:
#                print("\tsubbed", test, "for", self.name)
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
#    return collapseInt(self, lambda a,b: a+b)
    return collapseConstantInt(self)

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


@optimizes(ast.If)
def optimize(self):
    (cond, ifstmt) = self.children
    if isinstance(cond, ast.Boolean):
        if cond.val:
            return ifstmt
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


# not this is a special optimize which needs to set the loop status before optimizing children
def optimizeWhile(self):
    self.context.program.optimizerInLoop += 1

#    print ("optimizing while", self.children)

    self.children = tuple(map(lambda child: child.optimize(), self.children))
    opt = self._optimize()

    self.context.program.optimizerInLoop -= 1 

    return opt
setattr(ast.While, 'optimize', optimizeWhile)


@optimizes(ast.While)
def optimize(self):
    (cond, stmt) = self.children
    if isinstance(cond, ast.Boolean) and not cond.val:
        temp = ast.Nop()
        temp.context = self.context
        return temp
    return self


@optimizes(ast.Assignment)
def optimize(self):
    (expr) = self.children
    if isinstance(expr, ast.Integer):
        self.context.declareConstVar(self.name, expr.val)
#        print("\t\tMapped", self.name, "=>", expr.val)
    else:
        self.context.declareConstVar(self.name, None)
#        print("\t\t", self.name, "no longer const", self.children)
    return self    


@optimizes(ast.Decl)
def optimize(self):
    if isinstance(self.typename, ast.BasicType) and isinstance(self.children[0], ast.Integer):
        # have a named variable with a constant value (a = 10, b = 15)
        self.context.declareConstVar(self.name, self.children[0].val)
#        print("\t\tFound", self.name, "=>", self.children[0].val)
    return self

@optimizes(ast.StmtList)
def optimize(self):
    (stmts) = self.children
    # Constant propogation (search for ID which are constant and pass constant instead of ID)

#    print ("StmtList")

    newstmts = []
    for stmt in stmts:
#        print ("\t-", stmt, stmt.children, self.context.program.optimizerInLoop)
        stmt = stmt.optimize()
        newstmts.append(stmt)

    self.children = newstmts
    return self

def optimizeStmtList(self):
    return self._optimize()
setattr(ast.StmtList, 'optimize', optimizeStmtList)


@optimizes(ast.MainClassDecl)
def optimize(self):
    # TODO call while change is happening
#    print('optimizing')
    return self


