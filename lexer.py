import re

# Token types
TOKENS = [
    ('COMMENT', r'#.*'),
    ('KEYWORD', r'\b(file|binary|write|append|read|all|readline|readlines|write_csv|from)\b'),
    ('STRING', r'"([^"]*)"'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('WHITESPACE', r'\s+'),
    ('UNKNOWN', r'.'),
]

class Token:
    def __init__(self, type, value, line):
        self.type = type
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, line={self.line})"

def lex(code):
    # Scans the input code and returns a list of tokens
    # Also, tracks line numbers for better error reporting
    tokens = []
    pos = 0
    line = 1
    while pos < len(code):
        match = None
        for type, pattern in TOKENS:
            regex = re.compile(pattern)
            match = regex.match(code, pos)
            if match:
                value = match.group(0)
                
                # Check for unknown chars before rasing an error
                if type == 'UNKNOWN':
                    raise SyntaxError(f"Tabulon Lexer Error: Unknown character '{value}' at line {line}")

                if type == 'STRING':
                    # Extract text inside of quotes
                    value = match.group(1)
                
                if type not in ['WHITESPACE', 'COMMENT']:
                    tokens.append(Token(type, value, line))
                
                # Count newlines to track line numbers
                line += value.count('\n')
                
                pos = match.end()
                break
        
        if not match:
            pos += 1
            
    return tokens
