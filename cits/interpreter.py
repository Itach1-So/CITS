"""
CITS Interpreter - Executes the AST
"""

import os
from typing import Any, List, Dict, Optional
from .ast import *

class CitsInterpreter:
    """Interpreter for CITS language"""
    
    def __init__(self):
        self.env: Dict[str, Any] = {}
        self.functions: Dict[str, FuncStmt] = {}
        self.program: Dict[int, Any] = {}
        self.line_numbers: List[int] = []
        self.running = True
        self.for_stack = []
        self.while_stack = []
        self.skip_stack = []
        self.return_value = None
    
    def add_line(self, line_num: int, stmt: Any):
        """Add a line to the program"""
        self.program[line_num] = stmt
        self.line_numbers = sorted(self.program.keys())
    
    def delete_line(self, line_num: int):
        """Delete a line from the program"""
        if line_num in self.program:
            del self.program[line_num]
            self.line_numbers = sorted(self.program.keys())
    
    def list_program(self):
        """List all program lines"""
        if not self.program:
            print("[*] No program loaded")
            return
        for line_num in self.line_numbers:
            stmt = self.program[line_num]
            if isinstance(stmt, tuple) and stmt[0] == 'RAW':
                print(f"{line_num} {stmt[1]}")
            else:
                print(f"{line_num} {stmt}")
    
    def clear(self):
        """Clear the program"""
        self.program.clear()
        self.line_numbers = []
        self.env.clear()
        self.functions.clear()
    
    def run(self):
        """Run the program"""
        self.running = True
        self.for_stack = []
        self.while_stack = []
        self.skip_stack = []
        self.return_value = None
        
        if not self.line_numbers:
            print("[*] No program to run")
            return
        
        i = 0
        while i < len(self.line_numbers) and self.running:
            line_num = self.line_numbers[i]
            stmt = self.program[line_num]
            
            # Handle IF skip
            if self.skip_stack and self.skip_stack[-1]:
                if isinstance(stmt, EndStmt):
                    self.skip_stack.pop()
                i += 1
                continue
            
            # Execute statement
            result = self.execute(stmt)
            
            # Handle flow control
            if isinstance(result, int):
                if result in self.line_numbers:
                    i = self.line_numbers.index(result)
                    continue
                else:
                    raise RuntimeError(f"Line {result} not found")
            elif result == 'GOTO_END':
                break
            
            i += 1
        
        if self.running:
            print("[*] Program ended")
    
    def execute(self, stmt) -> Any:
        """Execute a statement"""
        
        if isinstance(stmt, LetStmt):
            self.env[stmt.name] = self.evaluate(stmt.expr)
            
        elif isinstance(stmt, PrintStmt):
            values = [self.evaluate(e) for e in stmt.exprs]
            print(' '.join(self._format(v) for v in values))
            
        elif isinstance(stmt, IfStmt):
            if self.evaluate_condition(stmt.condition):
                for s in stmt.then_body:
                    self.execute(s)
            elif stmt.else_body:
                for s in stmt.else_body:
                    self.execute(s)
                    
        elif isinstance(stmt, ForStmt):
            start_val = self.evaluate(stmt.start)
            end_val = self.evaluate(stmt.end)
            step_val = self.evaluate(stmt.step) if stmt.step else 1
            
            self.env[stmt.var] = start_val
            
            while True:
                current = self.env[stmt.var]
                if step_val > 0 and current > end_val:
                    break
                if step_val < 0 and current < end_val:
                    break
                
                for s in stmt.body:
                    self.execute(s)
                
                self.env[stmt.var] = current + step_val
                
        elif isinstance(stmt, WhileStmt):
            while self.evaluate_condition(stmt.condition):
                for s in stmt.body:
                    self.execute(s)
                    
        elif isinstance(stmt, InputStmt):
            if stmt.prompt:
                print(stmt.prompt, end=' ')
            val = input()
            try:
                if '.' in val:
                    self.env[stmt.var_name] = float(val)
                else:
                    self.env[stmt.var_name] = int(val)
            except ValueError:
                self.env[stmt.var_name] = val
                
        elif isinstance(stmt, GotoStmt):
            return stmt.line_num
            
        elif isinstance(stmt, EndStmt):
            self.running = False
            return 'GOTO_END'
            
        elif isinstance(stmt, ClsStmt):
            os.system('cls' if os.name == 'nt' else 'clear')
            
        elif isinstance(stmt, FuncStmt):
            self.functions[stmt.name] = stmt
            
        elif isinstance(stmt, ReturnStmt):
            if stmt.expr:
                self.return_value = self.evaluate(stmt.expr)
            return 'RETURN'
            
        elif isinstance(stmt, FuncCall):
            return self.execute_function(stmt.name, stmt.args)
            
        return None
    
    def execute_function(self, name: str, args: List[Any]) -> Any:
        """Execute a user-defined function"""
        if name not in self.functions:
            raise RuntimeError(f"Function '{name}' not defined")
        
        func = self.functions[name]
        if len(args) != len(func.params):
            raise RuntimeError(f"Function '{name}' expects {len(func.params)} arguments")
        
        # Save current environment
        old_env = self.env.copy()
        
        # Set parameters
        for param, arg in zip(func.params, args):
            self.env[param] = self.evaluate(arg)
        
        self.return_value = None
        
        # Execute function body
        for stmt in func.body:
            result = self.execute(stmt)
            if result == 'RETURN':
                break
        
        # Restore environment
        self.env = old_env
        
        return self.return_value
    
    def evaluate(self, node) -> Any:
        """Evaluate an expression"""
        
        if isinstance(node, Num):
            return node.value
        elif isinstance(node, Str):
            return node.value
        elif isinstance(node, Var):
            if node.name not in self.env:
                raise RuntimeError(f"Variable '{node.name}' not defined")
            return self.env[node.name]
        elif isinstance(node, BinOp):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            
            op = node.op
            if op == 'PLUS':
                return left + right
            elif op == 'MINUS':
                return left - right
            elif op == 'TIMES':
                return left * right
            elif op == 'DIVIDE':
                if right == 0:
                    raise RuntimeError("Division by zero")
                return left / right
            elif op == 'POWER':
                return left ** right
        elif isinstance(node, UnaryOp):
            if node.op == 'NOT':
                return not self.evaluate(node.expr)
        elif isinstance(node, FuncCall):
            return self.execute_function(node.name, node.args)
        else:
            raise RuntimeError(f"Cannot evaluate: {type(node)}")
    
    def evaluate_condition(self, node) -> bool:
        """Evaluate a condition"""
        
        if isinstance(node, CompareOp):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            
            op = node.op
            if op == 'LT':
                return left < right
            elif op == 'GT':
                return left > right
            elif op == 'LE':
                return left <= right
            elif op == 'GE':
                return left >= right
            elif op == 'NE':
                return left != right
            elif op == 'EQ':
                return left == right
                
        elif isinstance(node, LogicOp):
            left = self.evaluate_condition(node.left)
            if node.op == 'AND':
                return left and self.evaluate_condition(node.right)
            elif node.op == 'OR':
                return left or self.evaluate_condition(node.right)
                
        elif isinstance(node, UnaryOp):
            if node.op == 'NOT':
                return not self.evaluate_condition(node.expr)
                
        else:
            return bool(self.evaluate(node))
        
        return False
    
    @staticmethod
    def _format(value) -> str:
        """Format value for output"""
        if isinstance(value, float):
            if value == int(value):
                return str(int(value))
            return str(value)
        return str(value)