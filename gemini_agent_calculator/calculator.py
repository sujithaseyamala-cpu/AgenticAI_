"""
Safe Arithmetic Calculator Engine for Agentic AI.
Built using Python's Abstract Syntax Tree (ast) to prevent arbitrary code execution (no eval vulnerabilities).
Supports: +, -, *, /, //, %, **, parentheses, and unary operations.
"""

import ast
import operator
from typing import Union, Dict, Any

# Supported binary operators
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

class SafeCalculator:
    """A secure, AST-based arithmetic expression evaluator."""

    @classmethod
    def evaluate(cls, expression: str) -> Union[int, float]:
        """
        Safely evaluates an arithmetic expression string.
        
        Examples:
            evaluate("2 + 3 * 4") -> 14
            evaluate("(100 - 25) / 5") -> 15.0
            evaluate("2 ** 8") -> 256
            evaluate("50 % 7") -> 1
        """
        if not expression or not expression.strip():
            raise ValueError("Expression cannot be empty.")

        # Clean common input quirks (e.g. '^' instead of '**')
        cleaned_expr = expression.replace("^", "**").strip()

        try:
            node = ast.parse(cleaned_expr, mode='eval')
        except SyntaxError as e:
            raise ValueError(f"Invalid arithmetic expression '{expression}': {str(e)}")

        return cls._eval_node(node.body)

    @classmethod
    def _eval_node(cls, node: ast.AST) -> Union[int, float]:
        # Numbers (ast.Constant in Python 3.8+)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant type: {type(node.value).__name__}")

        # Binary operations (a + b, a * b, etc.)
        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in SAFE_OPERATORS:
                raise ValueError(f"Unsupported operator: {op_type.__name__}")
            
            left = cls._eval_node(node.left)
            right = cls._eval_node(node.right)

            # Prevent Division By Zero
            if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right == 0:
                raise ZeroDivisionError("Division or modulo by zero is undefined.")

            # Prevent resource exhaustion with massive exponents (e.g., 9**999999)
            if op_type is ast.Pow and (right > 10000 or (isinstance(left, (int, float)) and abs(left) > 1000 and right > 100)):
                raise OverflowError("Exponent is too large to safely compute.")

            return SAFE_OPERATORS[op_type](left, right)

        # Unary operations (-5, +10)
        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in SAFE_OPERATORS:
                raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
            operand = cls._eval_node(node.operand)
            return SAFE_OPERATORS[op_type](operand)

        else:
            raise ValueError(f"Unsupported expression syntax: {type(node).__name__}")

# Explicit discrete operations for granular tool execution if needed
def add(a: float, b: float) -> float:
    """Adds two numbers."""
    return a + b

def subtract(a: float, b: float) -> float:
    """Subtracts b from a."""
    return a - b

def multiply(a: float, b: float) -> float:
    """Multiplies two numbers."""
    return a * b

def divide(a: float, b: float) -> float:
    """Divides a by b."""
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return a / b

def modulo(a: float, b: float) -> float:
    """Calculates remainder of a divided by b."""
    if b == 0:
        raise ZeroDivisionError("Cannot calculate modulo with divisor zero.")
    return a % b

def power(base: float, exponent: float) -> float:
    """Calculates base raised to the power of exponent."""
    if exponent > 10000:
        raise OverflowError("Exponent too large.")
    return base ** exponent
