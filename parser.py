import sys

class FileBlock:
    def __init__(self, filename, statements):
        self.filename = filename
        self.statements = statements

class BinaryBlock:
    def __init__(self, filename, statements):
        self.filename = filename
        self.statements = statements

class WriteStatement:
    def __init__(self, content):
        self.content = content

class AppendStatement:
    def __init__(self, content):
        self.content = content

class ReadStatement:
    def __init__(self, target):
        self.target = target

class ReadLineStatement:
    def __init__(self):
        pass

class ReadLinesStatement:
    def __init__(self):
        pass

class WriteCsvStatement:
    def __init__(self, source_file):
        self.source_file = source_file

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        # Returns the current token without advancing the pos
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected_type=None, expected_value=None):
        # Validates and returns the current token, then advances
        token = self.peek()
        if not token:
            raise SyntaxError("Tabulon Parser Error: Unexpected end of input")
        
        if expected_type and token.type != expected_type:
            raise SyntaxError(f"Tabulon Parser Error: Expected {expected_type} at line {token.line}, got {token.type} ('{token.value}')")
        
        if expected_value and token.value != expected_value:
            raise SyntaxError(f"Tabulon Parser Error: Expected keyword '{expected_value}' at line {token.line}, got '{token.value}'")
            
        self.pos += 1
        return token

    def parse(self):
        # Entry point for parsing the entire script
        ast = []
        try:
            while self.peek():
                ast.append(self.parse_block())
        except SyntaxError as e:
            print(e)
            sys.exit(1)
        return ast

    def parse_block(self):
        # Parses a file or binary block
        keyword = self.consume('KEYWORD').value
        filename = self.consume('STRING').value
        self.consume('LBRACE')
        
        statements = []
        while self.peek() and self.peek().type != 'RBRACE':
            statements.append(self.parse_statement())
            
        self.consume('RBRACE')
        
        if keyword == 'file':
            return FileBlock(filename, statements)
        elif keyword == 'binary':
            return BinaryBlock(filename, statements)
        else:
            raise Exception(f"Unknown block type: {keyword}")

    def parse_statement(self):
        # Parses individual statements inside a block
        keyword = self.consume('KEYWORD').value
        
        if keyword == 'write':
            content = self.consume('STRING').value
            return WriteStatement(content)
        
        elif keyword == 'append':
            content = self.consume('STRING').value
            return AppendStatement(content)
        
        elif keyword == 'read':
            target = self.consume('KEYWORD', 'all').value
            return ReadStatement(target)
        
        elif keyword == 'readline':
            return ReadLineStatement()
        
        elif keyword == 'readlines':
            return ReadLinesStatement()
        
        elif keyword == 'write_csv':
            self.consume('KEYWORD', 'from')
            source_file = self.consume('STRING').value
            return WriteCsvStatement(source_file)
        
        else:
            raise Exception(f"Unknown statement: {keyword}")
