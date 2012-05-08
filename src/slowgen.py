'''
Code generation routines that generate more traditional
for a compiler
'''

from codegen import codegens
from code import CodeGen, CmpOp, Flags
import ast

@codegens(ast.Program)
def codegen(self, c):
    mainclass, *classes = self.children
    
    c.setLine(1)

    #TODO other methods
    
    #make main function
    main = CodeGen(c.filename, 'main')
    main.context = mainclass.context
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
    stmts = self.children

    c.varnames = ['_locals']
    c.BUILD_LIST()
    c.STORE_FAST('_locals')

    for stmt in stmts:
        stmt.codegen(c)
    
    c.LOAD_CONST(None)
    c.RETURN_VALUE()

@codegens(ast.StmtList)
def codegen(self, c):
    stmts = self.children

    context = self.context
    methodContext = context.method

    #remember how many locals we had
    nLocals = len(methodContext.localVars)

    for s in stmts:
        s.codegen(c)

    #delete unneeded locals
    c.LOAD_FAST('_locals')
    c.LOAD_CONST(None)
    c.LOAD_CONST(nLocals)
    c.BUILD_SLICE()
    c.BINARY_SUBSCR()
    c.STORE_FAST('_locals')

    methodContext.localVars = methodContext.localVars[:nLocals]

@codegens(ast.Decl)
def codegen(self, c):
    (expr,) = self.children
    
    context = self.context
    methodContext = context.method
    classContext = context.classContext
    vartype = classContext.varType(self.name)
    #TODO fields

    c.LOAD_FAST('_locals')
    c.LOAD_ATTR('append')
    expr.codegen(c)
    c.CALL_FUNCTION(1)
    methodContext.localVars.append(self.name)

@codegens(ast.Assignment)
def codegen(self, c):
    (expr,) = self.children
    
    context = self.context
    methodContext = context.method
    classContext = context.classContext
    typename = classContext.varType(self.name)
    #TODO fields

    expr.codegen(c)
    c.LOAD_FAST('_locals')
    c.LOAD_CONST(methodContext.localVars.index(self.name))
    c.STORE_SUBSCR()

@codegens(ast.ID)
def codegen(self, c):
    context = self.context
    methodContext = context.method
    classContext = context.classContext
    typename = classContext.varType(self.name)
    #TODO fields

    c.LOAD_FAST('_locals')
    c.LOAD_CONST(methodContext.localVars.index(self.name))
    c.BINARY_SUBSCR()

@codegens(ast.If)
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

    # Store the place to jump back to
    beforeCond = c.marker()

    # Codegen the condition
    cond.codegen(c)

    # Write the jump instruction
    jumpLoc = c.POP_JUMP_IF_FALSE()

    # Codegen the stmt
    stmt.codegen(c)

    # Jump back to before the cond
    c.JUMP_ABSOLUTE(beforeCond)

    # Mark the end of the while loop
    jumpLoc()

print('WARNING: slowgen codegen not fully implemented')

