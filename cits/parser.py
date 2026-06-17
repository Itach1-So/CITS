"""
CITS Parser - Parses tokens into AST
"""

from typing import List, Any, Optional
from .lexer import Token
from .ast import *

class CitsParser:
    """Parser for CITS language"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def peek(self) -> Optional[Token]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    
    def consume(self, expected_type: str = None) -> Token:
        token = self.peek()
        if token is None:
            raise SyntaxError(f"Unexpected end of input, expected {expected_type}")
        if expected_type and token.type != expected_type:
            raise SyntaxError(f"Expected {expected_type}, got {token.type} at line {token.line}")
        self.pos += 1
        return token
    
    def parse_program(self) -> List[Any]:
        """Parse entire program"""
        statements = []
        while self.peek():
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            # Skip newlines
            while self.peek() and self.peek().type == 'NEWLINE':
                self.consume()
        return statements
    
    def parse_statement(self) -> Optional[Any]:
        """Parse a single statement"""
        token = self.peek()
        
        if token is None:
            return None
        
        if token.type == 'LET':
            return self.parse_let()
        elif token.type == 'PRINT':
            return self.parse_print()
        elif token.type == 'IF':
            return self.parse_if()
        elif token.type == 'FOR':
            return self.parse_for()
        elif token.type == 'WHILE':
            return self.parse_while()
        elif token.type == 'INPUT':
            return self.parse_input()
        elif token.type == 'GOTO':
            return self.parse_goto()
        elif token.type == 'END':
            self.consume()
            return EndStmt()
        elif token.type == 'CLS':
            self.consume()
            return ClsStmt()
        elif token.type == 'FUNC':
            return self.parse_func()
        elif token.type == 'RETURN':
            return self.parse_return()
        else:
            # If it's not a keyword, treat as expression
            expr = self.parse_expression()
            return expr
    
    def parse_let(self) -> LetStmt:
        self.consume('LET')
        name = self.consume('IDENTIFIER').value
        self.consume('EQ')
        expr = self.parse_expression()
        return LetStmt(name, expr)
    
    def parse_print(self) -> PrintStmt:
        self.consume('PRINT')
        exprs = []
        while self.peek() and self.peek().type != 'NEWLINE':
            exprs.append(self.parse_expression())
            if self.peek() and self.peek().type == 'COMMA':
                self.consume('COMMA')
            else:
                break
        return PrintStmt(exprs)
    
    def parse_if(self) -> IfStmt:
        self.consume('IF')
        condition = self.parse_condition()
        self.consume('THEN')
        
        # Parse then body
        then_body = []
        self.consume('NEWLINE')
        while self.peek() and self.peek().type != 'ELSE' and self.peek().type != 'ENDIF':
            if self.peek().type == 'NEWLINE':
                self.consume('NEWLINE')
                continue
            stmt = self.parse_statement()
            if stmt:
                then_body.append(stmt)
        
        # Check for ELSE
        else_body = None
        if self.peek() and self.peek().type == 'ELSE':
            self.consume('ELSE')
            else_body = []
            self.consume('NEWLINE')
            while self.peek() and self.peek().type != 'ENDIF':
                if self.peek().type == 'NEWLINE':
                    self.consume('NEWLINE')
                    continue
                stmt = self.parse_statement()
                if stmt:
                    else_body.append(stmt)
        
        self.consume('ENDIF')
        return IfStmt(condition, then_body, else_body)
    
    def parse_for(self) -> ForStmt:
        self.consume('FOR')
        var = self.consume('IDENTIFIER').value
        self.consume('EQ')
        start = self.parse_expression()
        self.consume('TO')
        end = self.parse_expression()
        
        step = Num(1)
        if self.peek() and self.peek().type == 'STEP':
            self.consume('STEP')
            step = self.parse_expression()
        
        # Parse body
        body = []
        self.consume('NEWLINE')
        while self.peek() and self.peek().type != 'NEXT':
            if self.peek().type == 'NEWLINE':
                self.consume('NEWLINE')
                continue
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        
        self.consume('NEXT')
        if self.peek() and self.peek().type == 'IDENTIFIER':
            self.consume('IDENTIFIER')
        
        return ForStmt(var, start, end, step, body)
    
    def parse_while(self) -> WhileStmt:
        self.consume('WHILE')
        condition = self.parse_condition()
        
        body = []
        self.consume('NEWLINE')
        while self.peek() and self.peek().type != 'WEND':
            if self.peek().type == 'NEWLINE':
                self.consume('NEWLINE')
                continue
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        
        self.consume('WEND')
        return WhileStmt(condition, body)
    
    def parse_input(self) -> InputStmt:
        self.consume('INPUT')
        
        prompt = None
        if self.peek() and self.peek().type == 'STRING':
            prompt = self.consume('STRING').value
            self.consume('COMMA')
        
        var_name = self.consume('IDENTIFIER').value
        return InputStmt(var_name, prompt)
    
    def parse_goto(self) -> GotoStmt:
        self.consume('GOTO')
        line_num = self.consume('NUMBER').value
        return GotoStmt(int(line_num))
    
    def parse_func(self) -> FuncStmt:
        self.consume('FUNC')
        name = self.consume('IDENTIFIER').value
        self.consume('LPAREN')
        
        params = []
        if self.peek() and self.peek().type != 'RPAREN':
            params.append(self.consume('IDENTIFIER').value)
            while self.peek() and self.peek().type == 'COMMA':
                self.consume('COMMA')
                params.append(self.consume('IDENTIFIER').value)
        
        self.consume('RPAREN')
        self.consume('NEWLINE')
        
        body = []
        while self.peek() and self.peek().type != 'END':
            if self.peek().type == 'NEWLINE':
                self.consume('NEWLINE')
                continue
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        
        self.consume('END')
        return FuncStmt(name, params, body)
    
    def parse_return(self) -> ReturnStmt:
        self.consume('RETURN')
        if self.peek() and self.peek().type != 'NEWLINE':
            expr = self.parse_expression()
            return ReturnStmt(expr)
        return ReturnStmt()
    
    def parse_condition(self) -> Any:
        return self.parse_or()
    
    def parse_or(self) -> Any:
        left = self.parse_and()
        while self.peek() and self.peek().type == 'OR':
            self.consume('OR')
            right = self.parse_and()
            left = LogicOp('OR', left, right)
        return left
    
    def parse_and(self) -> Any:
        left = self.parse_not()
        while self.peek() and self.peek().type == 'AND':
            self.consume('AND')
            right = self.parse_not()
            left = LogicOp('AND', left, right)
        return left
    
    def parse_not(self) -> Any:
        if self.peek() and self.peek().type == 'NOT':
            self.consume('NOT')
            expr = self.parse_not()
            return UnaryOp('NOT', expr)
        return self.parse_comparison()
    
    def parse_comparison(self) -> Any:
        left = self.parse_expression()
        
        if self.peek() and self.peek().type in ['LT', 'GT', 'LE', 'GE', 'NE', 'EQ']:
            op_token = self.consume()
            right = self.parse_expression()
            return CompareOp(op_token.type, left, right)
        
        return left
    
    def parse_expression(self) -> Any:
        return self.parse_add_sub()
    
    def parse_add_sub(self) -> Any:
        left = self.parse_mul_div()
        
        while self.peek() and self.peek().type in ['PLUS', 'MINUS']:
            op = self.consume()
            right = self.parse_mul_div()
            left = BinOp(op.type, left, right)
        
        return left
    
    def parse_mul_div(self) -> Any:
        left = self.parse_power()
        
        while self.peek() and self.peek().type in ['TIMES', 'DIVIDE']:
            op = self.consume()
            right = self.parse_power()
            left = BinOp(op.type, left, right)
        
        return left
    
    def parse_power(self) -> Any:
        left = self.parse_atom()
        
        while self.peek() and self.peek().type == 'POWER':
            self.consume('POWER')
            right = self.parse_atom()
            left = BinOp('POWER', left, right)
        
        return left
    
    def parse_atom(self) -> Any:
        token = self.peek()
        
        if token.type == 'NUMBER':
            self.consume()
            return Num(token.value)
        elif token.type == 'STRING':
            self.consume()
            return Str(token.value)
        elif token.type == 'IDENTIFIER':
            self.consume()
            # Check if it's a function call
            if self.peek() and self.peek().type == 'LPAREN':
                self.consume('LPAREN')
                args = []
                if self.peek() and self.peek().type != 'RPAREN':
                    args.append(self.parse_expression())
                    while self.peek() and self.peek().type == 'COMMA':
                        self.consume('COMMA')
                        args.append(self.parse_expression())
                self.consume('RPAREN')
                return FuncCall(token.value, args)
            return Var(token.value)
        elif token.type == 'LPAREN':
            self.consume('LPAREN')
            expr = self.parse_expression()
            self.consume('RPAREN')
            return expr
        else:
            raise SyntaxError(f"Unexpected token: {token.type} at line {token.line}")