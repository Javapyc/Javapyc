# Implementation Language

We have decided to use CPython 3 as our implementation language for various
reasons: 
- It contains modules that can automatically serialize and parse any code that
  we generate into pyc files
- The CPython version we use will provide information about op codes and other
  useful information for generating code
- The focus of this class is to explore the fundamental concepts that are
  required for a compiler.  Using Python allows us to focus only on the details
  that matter

# Scanner Generator

Python has a considerable number of scanner generator libraries available.  For
this project, we have decided to use Spark, which provides a simple, pythonic
way to define tokens and syntax to generate tokens and parse trees.

# Lexer Example Location

An example of our lexer in action can be found at
`/trunk/SparkTest/simplescanner.py`.

