'''
Code generation routines that generate more traditional
for a compiler
'''

from codegen import codegens
from code import CodeGen, CmpOp, Flags
import ast

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

raise Exception('slowgen codegen not implemented')

