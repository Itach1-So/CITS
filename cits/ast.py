"""
CITS AST - Abstract Syntax Tree Nodes
"""

from dataclasses import dataclass
from typing import List, Optional, Any

# ============ Statement Nodes ============

@dataclass
class LetStmt:
    """LET variable = expression"""
    name: str
    expr: Any

@dataclass
class PrintStmt:
    """PRINT expression1, expression2, ..."""
    exprs: List[Any]

@dataclass
class IfStmt:
    """IF condition THEN ... ELSE ... ENDIF"""
    condition: Any
    then_body: List[Any]
    else_body: Optional[List[Any]] = None

@dataclass
class ForStmt:
    """FOR variable = start TO end STEP step ... NEXT"""
    var: str
    start: Any
    end: Any
    step: Any
    body: List[Any] = None

@dataclass
class WhileStmt:
    """WHILE condition ... WEND"""
    condition: Any
    body: List[Any] = None

@dataclass
class InputStmt:
    """INPUT prompt, variable"""
    var_name: str
    prompt: Optional[str] = None

@dataclass
class GotoStmt:
    """GOTO line_number"""
    line_num: int

@dataclass
class EndStmt:
    """END - Stop program"""
    pass

@dataclass
class ClsStmt:
    """CLS - Clear screen"""
    pass

@dataclass
class FuncStmt:
    """FUNC name(params) ... END"""
    name: str
    params: List[str]
    body: List[Any]

@dataclass
class ReturnStmt:
    """RETURN expression"""
    expr: Optional[Any] = None

# ============ Expression Nodes ============

@dataclass
class BinOp:
    """Binary operation: left op right"""
    op: str
    left: Any
    right: Any

@dataclass
class UnaryOp:
    """Unary operation: op expr"""
    op: str
    expr: Any

@dataclass
class CompareOp:
    """Comparison: left op right"""
    op: str
    left: Any
    right: Any

@dataclass
class LogicOp:
    """Logic operation: left op right (AND/OR)"""
    op: str
    left: Any
    right: Any

@dataclass
class Num:
    """Number literal"""
    value: float

@dataclass
class Str:
    """String literal"""
    value: str

@dataclass
class Var:
    """Variable reference"""
    name: str

@dataclass
class FuncCall:
    """Function call: name(args)"""
    name: str
    args: List[Any]