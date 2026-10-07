"""
Alternative Implementation using the official Google GenAI SDK (google-genai).
Shows how to configure tools using google.genai types without any third-party frameworks.
"""

import os
from typing import Optional
from google import genai
from google.genai import types
from calculator import SafeCalculator, add, subtract, multiply, divide, modulo, power
from tools import execute_tool_call

def calculate_expression(expression: str) -> str:
    """Evaluates an arithmetic expression with +, -, *, /, //, %, ** and parentheses."""
    res = execute_tool_call("calculate_expression", {"expression": expression})
    return str(res.get("result", res.get("error")))

def basic_arithmetic(operation: str, a: float, b: float) -> str:
    """Performs an arithmetic operation (add, subtract, multiply, divide, modulo, power) between two numbers."""
    res = execute_tool_call("basic_arithmetic", {"operation": operation, "a": a, "b": b})
    return str(res.get("result", res.get("error")))

class GeminiSDKCalculatorAgent:
    """Agent using the official google-genai SDK with automatic/manual function calling."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-3.8-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model = model
        # Pass Python functions directly to GenAI SDK; it automatically derives JSON schema
        self.chat_session = self.client.chats.create(
            model=self.model,
            config=types.GenerateContentConfig(
                tools=[calculate_expression, basic_arithmetic],
                temperature=0.0,
                system_instruction=(
                    "You are a calculation agent. Always use calculate_expression or basic_arithmetic tools "
                    "for any arithmetic operation. Do not compute math in your head."
                )
            )
        )

    def chat(self, prompt: str) -> str:
        response = self.chat_session.send_message(prompt)
        return response.text
