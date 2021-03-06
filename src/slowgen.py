'''
Code generation routines that generate more traditional
for a compiler

Object representation:
An object is represented by a list, where the first element is the name of the class.
The following elements are the fields of the class hierarchy, starting with the parent.

For example, if a class A extends B, and A contains an int field and B contains a boolean field,
an instance of A could be represented by ['A', False, 0].  An instance could be represented by
['B', False].

All instance methods accept a 'self' parameter and any named arguments that are passed.  A
method stores all parameters and local variables in a list called '_locals', which is appended
to as variables are declared and popped from as scopes are left.

'''

from codegen import codegens
from code import CodeGen, CmpOp, Flags
import ast

@codegens(ast.Program)
def codegen(self, c):
    mainclass, *classes = self.children

    c.setLine(1)

    for cls in classes:
        cls.codegen(c)
    
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

@codegens(ast.ClassDecl)
def codegen(self, c):
    for method in self.children:
        methodname = '{0}__{1}'.format(self.name, method.ID)
        func = CodeGen(c.filename, methodname)
        func.setFlags(Flags.NEWLOCALS | Flags.OPTIMIZED)
        func.argcount = len(method.formallist)+1
        func.varnames = ['self'] + list(map(lambda formal: formal.ID, method.formallist))
        method.codegen(func)
        c.LOAD_CONST(func)
        c.MAKE_FUNCTION()
        c.STORE_NAME(methodname)

@codegens(ast.MethodDecl)
def codegen(self, c):
    
    *stmts, expr = self.children

    c.setLine(1)

    params = list(map(lambda formal: formal.ID, self.formallist))
    c.varnames = ['self'] + params + ['_locals'] # NOTE: order is important here!
    for formal in self.formallist:
        c.LOAD_FAST(formal.ID) # also creates these variables in fast list
    c.BUILD_LIST(len(self.formallist))
    c.STORE_FAST('_locals')

    # Build localVars list to be in parallel with _locals
    self.context.localVars = params

    for stmt in stmts:
        stmt.codegen(c)
    
    expr.codegen(c)
    c.RETURN_VALUE()

@codegens(ast.Call)
def codegen(self, c):
    obj, *args = self.children
    func = self.func

    objType = obj.typecheck(self.context)
    
    # Get funcName from vtable here
    # pseudocode...
    # self := _locals[0]
    # funcName := self[0][func]

    obj.codegen(c)
    c.DUP_TOP()

    # Put globals dict on top of the stack
    c.LOAD_GLOBAL('globals')
    c.CALL_FUNCTION(0)

    # put "this" on top of the stack
    c.ROT_TWO()
    
    # Now get the vtable on the top of the stack
    c.LOAD_CONST(0)
    c.BINARY_SUBSCR()

    # Apply the key (func) to get the value (<class>__<func>) on TOS
    c.LOAD_CONST(func) 
    c.BINARY_SUBSCR()

    # Subscript globals (map) with <class>__<func>
    # TOS will be the code object with that name
    c.BINARY_SUBSCR()

    # To put "this" on top of the stack
    # needed for function call
    c.ROT_TWO()
       
    for arg in args:
        arg.codegen(c)

    c.CALL_FUNCTION(len(args)+1)

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

    # Add the new variable to _locals
    c.LOAD_FAST('_locals')
    c.LOAD_ATTR('append')
    expr.codegen(c)
    c.CALL_FUNCTION(1)
    c.POP_TOP() # to remove None

    # Add it to the parallel copy of localVars
    methodContext.localVars.append(self.name)

@codegens(ast.Assignment)
def codegen(self, c):
    (expr,) = self.children
    
    context = self.context
    methodContext = context.method
    classContext = context.classContext
    typename = classContext.varType(self.name)
    
    if self.name in methodContext.localVars:
        expr.codegen(c)
        c.LOAD_FAST('_locals')
        c.LOAD_CONST(methodContext.localVars.index(self.name))
        c.STORE_SUBSCR()
    else:
        expr.codegen(c)
        index = classContext.fields.index(self.name) 
        c.LOAD_FAST('self')
        c.LOAD_CONST(1 + index)
        c.STORE_SUBSCR()

@codegens(ast.ID)
def codegen(self, c):
    context = self.context
    methodContext = context.method
    classContext = context.classContext
    typename = classContext.varType(self.name)

    if self.name in methodContext.localVars:
        c.LOAD_FAST('_locals')
        c.LOAD_CONST(methodContext.localVars.index(self.name))
        c.BINARY_SUBSCR()
    else:
        index = classContext.fields.index(self.name)
        c.LOAD_FAST('self')
        c.LOAD_CONST(1 + index)
        c.BINARY_SUBSCR()

@codegens(ast.NewInstance)
def codegen(self, c):
    ''' Represent an instance with a list of the form:
        [ vtable, field1, field2, ...]
    '''

    context = self.context
    program = context.program

    classContext = program.lookupClass(self.name)

    methods = {}
    while (classContext):
        for m in classContext.methods:
            if m.name not in methods:
                methods[m.name] = "{0}__{1}".format(classContext.name, m.name)
        classContext = classContext.parent

    c.BUILD_MAP(len(methods)) 

    for method in methods:
        c.LOAD_CONST(methods[method]) # value
        c.LOAD_CONST(method) # key
        c.STORE_MAP()

    classContext = program.lookupClass(self.name)

    for field in classContext.classvarsAndParent:
        vartype = field.typename
        if vartype == ast.IntType:
            c.LOAD_CONST(0)
        elif vartype == ast.BoolType:
            c.LOAD_CONST(False)
        else:
            c.LOAD_CONST(None)

    c.BUILD_LIST(1 + len(classContext.classvarsAndParent))
    # import pdb; pdb.set_trace()

@codegens(ast.This)
def codegen(self, c):
    c.LOAD_FAST('self')

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

