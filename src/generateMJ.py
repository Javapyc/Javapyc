#!/usr/bin/python
import random

delimiters = [';', '.', ',', '=', '(', ')', '{', '}', '[', ']']
operators = ['+', '-', '*', '/', '<', '<=', '>=', '>', '==', '!=', '&&', '||', '!']
reservedwords = ["class", "public", "static", "extends", "void", "int", "boolean", "if", "else", "while", "return", "null", "true", "false", "this", "new", "String", "main", "System.out.println"]
digit = list(range(10))
whitespace = ["\n", "\t", " "]
nonzero = list(range(1, 10))
letter = list(map(chr, list(range(97, 123)) + list(range(65, 91))))

def getID():
	f = random.choice(letter)
	ln = random.randrange(1, 16)	
	for i in range(ln):
		w = random.choice([letter, digit])
		f += str(random.choice(w))
	return "ID", f

def getInt():
	if	random.random() > 0.9:
		return ("Integer", 0)
	f = str(random.choice(nonzero))
	ln = random.randrange(1, 16)	
	for i in range(ln):
		f += str(random.choice(digit))
	return "Integer", int(f)

def getReservedWord():
	return "ReservedWord", random.choice(reservedwords)

def getOperator():
	return "Operator", random.choice(operators)

def getDelimiter():
	return "Delimiter", random.choice(delimiters)

def getWS():
	return "Whitespace", random.choice(whitespace)

allThings = [getID, getInt, getReservedWord, getOperator, getDelimiter, getWS]

def getCommentString():
	f = ""
	for i in range(7):
		token = random.choice(list(filter(lambda s: s is not getWS, allThings)))
		f += str(token()[1]) + " "
	return f

spaceSensitive  = ["ReservedWord", "ID", "Integer"]

for j in range(100):
	outcode = open("tests/fakecode" + str(j) + ".java", 'w')
	outlabel = open("tests/fakecode" + str(j) + ".lexout", 'w')

	# Just pick one that doesn't require a space
	last = "Operator"

	# We want 100 tokens
	for i in range(100):
		token = random.choice(allThings)
		val = token()
		sep = ""
		if val[0] in spaceSensitive and last in spaceSensitive:
			sep = " "

		outcode.write(sep + str(val[1]))
		last = val[0]

		# Write comments in every now and again
		if random.random() > 0.96:
			if random.random() > 0.5:
				outcode.write("/**")
				for t in range(3):
					outcode.write(getCommentString() + "\n")
				outcode.write("*/")
			else:
				outcode.write("//")
				outcode.write(getCommentString())
				outcode.write("\n")

		if val[0] is not "Whitespace":
			outlabel.write(val[0] + ", " + str(val[1]) + "\n")
	
	outcode.close()
	outlabel.close()




	


