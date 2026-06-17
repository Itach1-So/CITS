"""
CITS Lexer - Lexical Analyzer
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

@dataclass
class Token:
    type: str
    value: any
    line: int = 1
    column: int = 1
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}')"

class CitsLexer:
    """Lexical analyzer for CITS language"""
    
    def __init__(self):
        # Token patterns (order matters - keywords first!)
        self.patterns: List[Tuple[str, str]] = [
            # Keywords
            ('LET', r'\bLET\b'),
            ('PRINT', r'\bPRINT\b'),
            ('IF', r'\bIF\b'),
            ('THEN', r'\bTHEN\b'),
            ('ELSE', r'\bELSE\b'),
            ('ENDIF', r'\bENDIF\b'),
            ('FOR', r'\bFOR\b'),
            ('TO', r'\bTO\b'),
            ('STEP', r'\bSTEP\b'),
            ('NEXT', r'\bNEXT\b'),
            ('WHILE', r'\bWHILE\b'),
            ('WEND', r'\bWEND\b'),
            ('INPUT', r'\bINPUT\b'),
            ('GOTO', r'\bGOTO\b'),
            ('END', r'\bEND\b'),
            ('CLS', r'\bCLS\b'),
            ('REM', r'\bREM\b'),
            ('AND', r'\bAND\b'),
            ('OR', r'\bOR\b'),
            ('NOT', r'\bNOT\b'),
            ('FUNC', r'\bFUNC\b'),
            ('RETURN', r'\bRETURN\b'),
            
            # Data types
            ('NUMBER', r'\b\d+\.\d+\b'),  # Float first
            ('NUMBER', r'\b\d+\b'),        # Integer
            ('STRING', r'"[^"]*"'),
            ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            
            # Operators
            ('EQ', r'='),
            ('PLUS', r'\+'),
            ('MINUS', r'-'),
            ('TIMES', r'\*'),
            ('DIVIDE', r'/'),
            ('POWER', r'\^'),
            
            # Comparison
            ('LE', r'<='),
            ('GE', r'>='),
            ('NE', r'<>'),
            ('LT', r'<'),
            ('GT', r'>'),
            
            # Symbols
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('COMMA', r','),
            ('COLON', r':'),
            ('SEMICOLON', r';'),
            
            # Whitespace and comments
            ('WHITESPACE', r'[ \t]+'),
            ('NEWLINE', r'\n'),
            ('COMMENT', r'//.*'),
        ]
        
        # Compile all patterns
        self.compiled_patterns = [(t, re.compile(p)) for t, p in self.patterns]
    
    def tokenize(self, code: str) -> List[Token]:
        """Convert source code to list of tokens"""
        tokens = []
        pos = 0
        line = 1
        column = 1
        
        while pos < len(code):
            matched = False
            
            for token_type, pattern in self.compiled_patterns:
                match = pattern.match(code, pos)
                if match:
                    text = match.group(0)
                    
                    # Skip whitespace and comments
                    if token_type not in ['WHITESPACE', 'COMMENT']:
                        # Process special token types
                        if token_type == 'NUMBER':
                            value = float(text) if '.' in text else int(text)
                        elif token_type == 'STRING':
                            value = text[1:-1]  # Remove quotes
                        else:
                            value = text
                        
                        tokens.append(Token(token_type, value, line, column))
                    
                    # Update position
                    pos = match.end()
                    column += len(text)
                    
                    # Handle newlines
                    if token_type == 'NEWLINE':
                        line += 1
                        column = 1
                    
                    matched = True
                    break
            
            if not matched:
                raise SyntaxError(f"Invalid character at line {line}, column {column}: '{code[pos]}'")
        
        return tokens

# Test the lexer
if __name__ == "__main__":
    code = """
    LET x = 10 + 5
    PRINT "Hello CITS!"
    IF x > 5 THEN
        PRINT "x is big"
    ENDIF
    """
    
    lexer = CitsLexer()
    tokens = lexer.tokenize(code)
    
    for token in tokens:
        print(token)