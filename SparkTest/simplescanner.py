from spark import *

class Token():
	def __init__(self, type, attr=None):
		self.type = type
		self.attr = attr

	def __repr__(self):
		if self.attr:
			return "(" + self.type + ", " + self.attr + ")"
		else:
			return self.type
	
class MiniJavaScanner(GenericScanner):
	def __init__(self):
		GenericScanner.__init__(self)
		
	def tokenize(self, input):
		self.rv = []
		GenericScanner.tokenize(self, input)
		return self.rv
    
	def t_whitespace(self, s):
		r' \s+ '
		pass

	def t_number(self, s):
		r' \d+\b '
		t = Token(type='Integer', attr=s)
		self.rv.append(t)

	def t_comment(self, s):
		r'(/\*\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)'
		pass

	def t_op(self, s):
		r' \+|\-|\* '
		t = Token(type='Operator', attr=s)
		self.rv.append(t)


	def t_delimiter(self, s):
		r' {|}|\(|\)|\[|\]|; '
		self.rv.append(Token('Delimiter', s))

	def t_ID(self, s):
		r' [a-zA-Z](\w|\d)* '
		self.rv.append(Token('ID', s))

class MiniJava2Scanner(MiniJavaScanner):
	''' Do this so that reserved words are checked first '''
	
	def t_reserved(self, s):
		r' System\.out\.println|public|static|void|String|class|main '
		self.rv.append(Token('ReservedWord', s))
		

def main():
	f = open("text.txt", 'r')
	input = f.read()
	scanner = MiniJava2Scanner()
	for token in scanner.tokenize(input):
		print token
	

main()




