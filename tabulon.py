import sys
from lexer import lex
from parser import Parser
from interpreter import Interpreter

def main():
    """Main CLI entry point for the Tabulon language."""
    if len(sys.argv) < 2:
        print("Usage: python tabulon.py <script.tbl>")
        return

    filename = sys.argv[1]
    
    # Read script content
    with open(filename, 'r') as f:
        code = f.read()

    # Tokenize the script
    try:
        tokens = lex(code)
    except SyntaxError as e:
        print(e)
        return

    # Parse tokens into AST
    parser = Parser(tokens)
    ast = parser.parse()

    # Execute the AST
    interpreter = Interpreter()
    interpreter.execute(ast)

if __name__ == "__main__":
    main()
