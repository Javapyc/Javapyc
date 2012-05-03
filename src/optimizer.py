
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


@optimizes(ast.If)
def optimie(self):
	(cond, ifstmt, elsestmt) = self.children
	if isinstance(cond, ast.Boolean):
		if cond.val:
			return ifstmt
		else:
			return elsestmt
	return self

@optimizes(ast.While)
def optimize(self):
	(cond, stmt) = self.children
	if isinstance(cond, ast.Boolean) and not cond.val:
		return ast.StmtList(tuple())
	return self


