'''
Code generation routines that provide a more direct
conversion to Python bytecode.
'''

from codegen import codegens
from code import CodeGen, CmpOp, Flags
import ast

@codegens(ast.Program)
def codegen(self, c):
    mainclass, *classes = self.children
    
    c.setLine(1)
    
    #codegen classes
    for cls in classes:
        cls.codegen(c)

    #make main function
    main = CodeGen(c.filename, 'main')
    main.setFlags(Flags.NEWLOCALS | Flags.OPTIMIZED)
    mainclass.codegen(main)
    c.LOAD_CONST(main)
    c.MAKE_FUNCTION()
    c.STORE_NAME('main')

    #ifmain
    c.LOAD_NAME('__name__')
    c.LOAD_CONST('__main__')
    c.COMPARE_OP(CmpOp.EQUAL)
    dest = c.POP_JUMP_IF_FALSE()
    c.LOAD_NAME('main')
    c.CALL_FUNCTION()
    c.POP_TOP()

    #module return
    dest()
    c.LOAD_CONST(None)
    c.RETURN_VALUE()

@codegens(ast.MainClassDecl)
def codegen(self, c):
    c.setLine(1)
    stmts = self.children
    for stmt in stmts:
        stmt.codegen(c)
    
    #return null;
    c.LOAD_CONST(None)
    c.RETURN_VALUE()

@codegens(ast.ClassDecl)
def codegen(self, c):
    c.LOAD_BUILD_CLASS()

    cls = CodeGen(c.filename, self.name)
    cls.setFlags(Flags.NEWLOCALS)
    cls.argcount = 1
    cls.setLine(1)
    cls.LOAD_FAST('__locals__')
    cls.STORE_LOCALS()
    cls.LOAD_NAME('__name__')
    cls.STORE_NAME('__module__')

    #define constructor to initialize class variables
    init = CodeGen(cls.filename, '__init__')
    init.setFlags(Flags.NEWLOCALS | Flags.OPTIMIZED)
    init.argcount = 1
    init.varnames = ['self']
    if self.parent:
        init.LOAD_GLOBAL(self.parent)
        init.LOAD_ATTR('__init__')
        init.LOAD_FAST('self')
        init.CALL_FUNCTION(1)
        init.POP_TOP()

    for var in self.classvars:
        vartype = var.typename
        if vartype == ast.IntType:
            init.LOAD_CONST(0)
        elif vartype == ast.BoolType:
            init.LOAD_CONST(False)
        else:
            init.LOAD_CONST(None)
        init.LOAD_FAST('self')
        init.STORE_ATTR('_' + var.ID)
    init.LOAD_CONST(None)
    init.RETURN_VALUE()
    cls.LOAD_CONST(init)
    cls.MAKE_FUNCTION()
    cls.STORE_NAME('__init__')

    #generate methods
    def genMethod(method, methodname):
        func = CodeGen(cls.filename, methodname)
        func.setFlags(Flags.NEWLOCALS | Flags.OPTIMIZED)
        func.argcount = len(method.formallist) + 1
        func.varnames = ['self'] + list(map(lambda formal: formal.ID, method.formallist))
        method.codegen(func)
        cls.LOAD_CONST(func)
        cls.MAKE_FUNCTION()
        cls.STORE_NAME(methodname)
    for method in self.children:
        genMethod(method, method.ID)
        if method.ID == 'toString':
            genMethod(method, '__str__')

    cls.LOAD_CONST(None)
    cls.RETURN_VALUE()

    c.LOAD_CONST(cls)
    c.MAKE_FUNCTION()

    c.LOAD_CONST(self.name)
    if self.parent:
        c.LOAD_GLOBAL(self.parent)
        c.CALL_FUNCTION(3)
    else:
        c.CALL_FUNCTION(2)
    c.STORE_NAME(self.name)

@codegens(ast.MethodDecl)
def codegen(self, c):
    c.setLine(1)
    *stmts, expr = self.children

    if self.isGenerator():
        c.setFlags(Flags.GENERATOR)

    for stmt in stmts:
        stmt.codegen(c)

    if expr:
        expr.codegen(c)
    else:
        c.LOAD_CONST(None)
    c.RETURN_VALUE()

@codegens(ast.StmtList)
def codegen(self, c):
    stmts = self.children
    for s in stmts:
        s.codegen(c)

@codegens(ast.Decl)
def codegen(self, c):
    (expr,) = self.children
    expr.codegen(c)
    
    context = self.context
    typename = context.localVarType(self.name)
    c.STORE_FAST(self.name)

@codegens(ast.Assignment)
def codegen(self, c):
    (expr,) = self.children
    expr.codegen(c)
    
    context = self.context
    typename = context.localVarType(self.name)
    if typename:
        c.STORE_FAST(self.name)
    else:
        c.LOAD_FAST('self')
        c.STORE_ATTR('_' + self.name)

@codegens(ast.Yield)
def codegen(self, c):
    (expr,) = self.children
    expr.codegen(c)

    c.YIELD_VALUE()
    c.POP_TOP()

@codegens(ast.If)
def codegen(self, c):
    cond, ifstmt = self.children
    cond.codegen(c)

    # binary array size coincides with binary location of instructions
    jumpLoc = c.POP_JUMP_IF_FALSE()

    # Codegen the ifstmt
    ifstmt.codegen(c)

    # Mark the jump to after the if block
    jumpLoc()

@codegens(ast.IfElse)
def codegen(self, c):
    cond, ifstmt, elsestmt = self.children
    cond.codegen(c)

    # binary array size coincides with binary location of instructions
    jumpLoc = c.POP_JUMP_IF_FALSE()

    # Codegen the ifstmt
    ifstmt.codegen(c)

    # Skip the else block
    endOfIf = c.JUMP_FORWARD()

    # Mark the jump to the else block
    jumpLoc()

    # Codegen the else stmt
    elsestmt.codegen(c)

    # Mark the end of the if statement
    endOfIf()


@codegens(ast.While)
def codegen(self, c):
    cond, stmt = self.children

    #Start the loop
    loop = c.SETUP_LOOP()

    #Condition
    loopStart = c.marker()
    cond.codegen(c)
    jumpEnd = c.POP_JUMP_IF_FALSE()

    #Body
    stmt.codegen(c)
    c.JUMP_ABSOLUTE(loopStart)

    #Loop end
    jumpEnd()
    c.POP_BLOCK()

    #Instruction position after loop
    loop()

@codegens(ast.Break)
def codegen(self, c):
    c.BREAK_LOOP()

@codegens(ast.NewInstance)
def codegen(self, c):
    c.LOAD_GLOBAL(self.name)
    c.CALL_FUNCTION()

@codegens(ast.This)
def codegen(self, c):
    c.LOAD_FAST('self')

@codegens(ast.ID)
def codegen(self, c):
    context = self.context
    typename = context.localVarType(self.name)
    if typename:
        c.LOAD_FAST(self.name)
    else:
        c.LOAD_FAST('self')
        c.LOAD_ATTR('_' + self.name)

@codegens(ast.Call)
def codegen(self, c):
    obj, *args = self.children
    func = self.func

    obj.codegen(c)
    c.LOAD_ATTR(func)

    for arg in args:
        arg.codegen(c)

    c.CALL_FUNCTION(len(args))

