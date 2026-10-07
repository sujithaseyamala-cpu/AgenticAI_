"""
tools.py - Calculator, Web Search, and Date/Time Tools in JSON format inside Python.
No extra frameworks. Pure standard Python + requests.
"""

import re
import datetime
import requests
from typing import Dict, Any
from rag_engine import search_students

# ==============================================================================
# 1. TOOL DEFINITIONS IN JSON FORMAT (Inside Python)
# Gemini receives these schemas to know when and how to call the tools.
# ==============================================================================

# Tool 1: Basic Calculator
CALCULATOR_TOOL_DEFINITION = {
    "name": "calculator",
    "description": "Performs basic arithmetic operations: addition, subtraction, multiplication, and division.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "operation": {
                "type": "STRING",
                "description": "The arithmetic operation to execute.",
                "enum": ["add", "subtract", "multiply", "divide"]
            },
            "a": {
                "type": "NUMBER",
                "description": "The first number."
            },
            "b": {
                "type": "NUMBER",
                "description": "The second number."
            }
        },
        "required": ["operation", "a", "b"]
    }
}

# Tool 2: Web Search
WEB_SEARCH_TOOL_DEFINITION = {
    "name": "web_search",
    "description": "Searches the web for facts, information, current events, definitions, and real-world knowledge.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "The search query string to search on the web (e.g. 'speed of light', 'highest mountain in the world')."
            }
        },
        "required": ["query"]
    }
}

# Tool 3: Date and Time
DATETIME_TOOL_DEFINITION = {
    "name": "get_current_datetime",
    "description": "Returns the current live date, time, day of the week, and year. Call this tool whenever the user asks for the current date, time, day, or asks 'what day is it today?'.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "timezone": {
                "type": "STRING",
                "description": "Optional timezone name like 'local' or 'UTC'. Defaults to 'local'."
            }
        }
    }
}

# Tool 4: Document Search (RAG over Student Database)
DOCUMENT_SEARCH_TOOL_DEFINITION = {
    "name": "document_search",
    "description": "Searches the uploaded student database document using RAG. Use this tool whenever the user asks questions about students, student details, marks (Python, DSA, AI, Overall), attendance, departments (CSE, IT, ECE, EEE, AIDS), placement eligibility, phone numbers, or emails.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "The search query (e.g. 'Priya Sharma', 'STU001', 'CSE department', 'attendance below 75%', 'highest overall mark', 'scored above 90 in AI', 'placement eligible')."
            }
        },
        "required": ["query"]
    }
}

# Combined Tools Schema sent to Gemini API
TOOLS_SCHEMA = [
    {
        "function_declarations": [
            CALCULATOR_TOOL_DEFINITION,
            WEB_SEARCH_TOOL_DEFINITION,
            DATETIME_TOOL_DEFINITION,
            DOCUMENT_SEARCH_TOOL_DEFINITION
        ]
    }
]


# ==============================================================================
# 2. TOOL EXECUTION LOGIC
# ==============================================================================

def run_calculator(operation: str, a: float, b: float) -> Dict[str, Any]:
    """
    Executes arithmetic operation and returns a JSON dictionary.
    """
    op = operation.lower().strip()
    
    if op == "add":
        result = a + b
    elif op == "subtract":
        result = a - b
    elif op == "multiply":
        result = a * b
    elif op == "divide":
        if b == 0:
            return {
                "status": "error",
                "message": "Error: Division by zero is undefined."
            }
        result = a / b
    else:
        return {
            "status": "error",
            "message": f"Unsupported operation: {operation}. Allowed: add, subtract, multiply, divide"
        }

    # Format cleanly (5.0 -> 5)
    if isinstance(result, float) and result.is_integer():
        result = int(result)

    return {
        "status": "success",
        "operation": op,
        "a": a,
        "b": b,
        "result": result
    }


def run_web_search(query: str) -> Dict[str, Any]:
    """
    Searches the web using lightweight HTTP requests (no extra frameworks).
    Queries DuckDuckGo and Wikipedia knowledge APIs.
    """
    query_str = query.strip()
    if not query_str:
        return {"status": "error", "message": "Search query cannot be empty."}

    results = []

    # 1. Query DuckDuckGo Instant Answers
    try:
        ddg_url = "https://api.duckduckgo.com/"
        params = {"q": query_str, "format": "json", "no_html": "1", "skip_disambig": "1"}
        res = requests.get(ddg_url, params=params, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if res.status_code == 200:
            data = res.json()
            if data.get("AbstractText"):
                results.append({
                    "title": data.get("Heading", "Summary"),
                    "snippet": data.get("AbstractText"),
                    "source": data.get("AbstractURL", "DuckDuckGo")
                })
            for topic in data.get("RelatedTopics", [])[:3]:
                if isinstance(topic, dict) and topic.get("Text"):
                    results.append({
                        "title": "Related Info",
                        "snippet": topic.get("Text"),
                        "source": topic.get("FirstURL", "DuckDuckGo")
                    })
    except Exception:
        pass

    # 2. Query Wikipedia Search API for detailed factual snippets
    if not results:
        try:
            wiki_url = "https://en.wikipedia.org/w/api.php"
            wiki_params = {
                "action": "query",
                "list": "search",
                "srsearch": query_str,
                "utf8": "",
                "format": "json",
                "srlimit": 3
            }
            res = requests.get(wiki_url, params=wiki_params, timeout=10, headers={"User-Agent": "AgenticSearch/1.0"})
            if res.status_code == 200:
                data = res.json()
                search_items = data.get("query", {}).get("search", [])
                for item in search_items:
                    clean_snippet = re.sub(r'<[^>]+>', '', item.get("snippet", ""))
                    results.append({
                        "title": item.get("title", ""),
                        "snippet": clean_snippet,
                        "source": f"https://en.wikipedia.org/wiki/{item.get('title', '').replace(' ', '_')}"
                    })
        except Exception as e:
            return {"status": "error", "message": f"Web search request failed: {e}"}

    if results:
        return {
            "status": "success",
            "query": query_str,
            "results": results
        }
    else:
        return {
            "status": "success",
            "query": query_str,
            "results": [],
            "message": f"No direct search results found for '{query_str}'."
        }


def run_get_datetime(timezone_str: str = "local") -> Dict[str, Any]:
    """
    Retrieves current date and time. Uses standard Python datetime (no extra frameworks).
    """
    now = datetime.datetime.now()
    utc_now = datetime.datetime.now(datetime.timezone.utc)

    return {
        "status": "success",
        "current_date": now.strftime("%Y-%m-%d"),
        "current_time": now.strftime("%H:%M:%S"),
        "day_of_week": now.strftime("%A"),
        "readable": now.strftime("%A, %B %d, %Y, %I:%M:%S %p"),
        "iso": now.isoformat(),
        "utc_time": utc_now.strftime("%Y-%m-%d %H:%M:%S UTC")
    }


def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dispatcher that routes an LLM tool call to the corresponding Python function.
    """
    if tool_name == "calculator":
        operation = tool_args.get("operation", "")
        a = float(tool_args.get("a", 0))
        b = float(tool_args.get("b", 0))
        return run_calculator(operation, a, b)

    elif tool_name == "web_search":
        query = tool_args.get("query", "")
        return run_web_search(query)

    elif tool_name == "get_current_datetime":
        timezone_str = tool_args.get("timezone", "local")
        return run_get_datetime(timezone_str)

    elif tool_name == "document_search":
        query = tool_args.get("query", "")
        return search_students(query)

    return {
        "status": "error",
        "message": f"Unknown tool: {tool_name}"
    }
