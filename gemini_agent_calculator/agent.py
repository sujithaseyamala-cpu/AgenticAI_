"""
agent.py - Pure Python Agentic AI Implementation (Zero Frameworks).
Demonstrates the fundamental ReAct / Tool-Calling loop using Google AI Studio Gemini LLM.
"""

import json
import time
import requests
from typing import Dict, Any, List
from tools import TOOLS_SCHEMA, execute_tool
from memory import ShortTermMemory


class BasicCalculatorAgent:
    """
    A lightweight, framework-free AI Agent that pairs Gemini LLM with RAG Document Search,
    Short-Term Memory, and Calculator tools.
    """

    def __init__(self, api_key: str, model: str = "gemini-flash-lite-latest"):
        """
        Initializes the agent with an API key, target Gemini model, and short-term memory.
        """
        self.api_key = api_key
        self.model = model
        self.endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        )
        
        # Short-term conversational memory
        self.memory = ShortTermMemory(window_size=10)

        # System prompt instructing Gemini on when to use each tool
        self.system_instruction = (
            "You are a helpful AI assistant equipped with four tools:\n"
            "1. 'document_search': use to search and retrieve student records from the uploaded student database (Student ID, Name, Dept, Year, Email, Phone, Attendance, Python, DSA, AI, Overall, Placement status).\n"
            "2. 'calculator': use for arithmetic operations (addition, subtraction, multiplication, division, averages, differences, counts).\n"
            "3. 'web_search': use to search the web for general knowledge and external facts.\n"
            "4. 'get_current_datetime': use to check current real-time date, time, year, or day.\n\n"
            "When answering questions about students, ALWAYS call 'document_search'. "
            "If asked to calculate or count student data, use 'document_search' to get the numbers, then use 'calculator' if needed. "
            "You have short-term memory: if the user asks a follow-up question (e.g. 'her phone number', 'his DSA mark'), refer to the student mentioned in previous conversation context."
        )

        # Multi-turn conversation memory for Gemini API
        self.history: List[Dict[str, Any]] = []

    def _call_gemini(self, contents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Low-level HTTP POST request to Google AI Studio REST API.
        Sends conversation contents along with the JSON tools schema.
        """
        payload = {
            "contents": contents,
            "tools": TOOLS_SCHEMA,
            "system_instruction": {
                "parts": [{"text": self.system_instruction}]
            },
            "generation_config": {
                "temperature": 0.0  # Zero temperature for deterministic reasoning
            }
        }
        headers = {"Content-Type": "application/json"}

        candidate_models = [self.model]
        for fallback in ["gemini-3-flash-preview", "gemini-2.0-flash", "gemini-3.8-flash"]:
            if fallback not in candidate_models:
                candidate_models.append(fallback)

        last_error = ""
        for model_name in candidate_models:
            endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
            for attempt in range(1, 4):
                try:
                    # 10s connection timeout, 90s read timeout for LLM inference
                    response = requests.post(endpoint, headers=headers, json=payload, timeout=(10, 90))
                    if response.status_code == 200:
                        return response.json()
                    elif response.status_code in (503, 429):
                        print(f"    [Notice]: {model_name} busy (HTTP {response.status_code}), retrying in {attempt * 2}s...")
                        time.sleep(2 * attempt)
                        continue
                    elif response.status_code == 404:
                        break  # Try next candidate model
                    else:
                        raise RuntimeError(f"Gemini API error [{response.status_code}]: {response.text}")
                except requests.exceptions.Timeout:
                    print(f"    [Notice]: {model_name} response timed out, retrying attempt {attempt}/3...")
                    last_error = f"Read timeout on {model_name}"
                    time.sleep(2 * attempt)
                except requests.RequestException as e:
                    last_error = str(e)
                    time.sleep(2 * attempt)

        raise RuntimeError(f"Network / API Error: {last_error}. Please check your connection or try again.")

    def run(self, user_message: str) -> str:
        """
        The Core Agentic Loop:
        1. Append user prompt to memory.
        2. Query Gemini with the prompt and tool definition.
        3. Check if Gemini asks to call the tool ('functionCall').
        4. If yes -> Execute Python tool with LLM inputs -> Send result back in JSON.
        5. Repeat until Gemini returns the final natural language answer.
        """
        print(f"\n[1. User Input]: {user_message}")

        # Step 1: Add user message to conversation memory
        self.memory.add_turn("user", user_message)
        self.history.append({
            "role": "user",
            "parts": [{"text": user_message}]
        })

        max_steps = 5  # Prevent infinite loops
        step = 0

        while step < max_steps:
            step += 1

            # Step 2: Call Gemini API
            print(f"[2. Agent Thinking]: Querying Gemini ({self.model})...")
            response = self._call_gemini(self.history)

            candidates = response.get("candidates", [])
            if not candidates:
                return "No response received from Gemini."

            candidate_content = candidates[0].get("content", {})
            parts = candidate_content.get("parts", [])

            # Check if Gemini returned a functionCall part
            function_calls = [p["functionCall"] for p in parts if "functionCall" in p]

            if not function_calls:
                # No tool was requested: Gemini has answered the question
                final_text = "".join(p.get("text", "") for p in parts if "text" in p)
                self.history.append({
                    "role": "model",
                    "parts": parts
                })
                self.memory.add_turn("assistant", final_text)
                print("[5. Final Answer Generated]")
                return final_text

            # Step 3: LLM requested a tool call!
            # Save the model's tool call turn to history
            self.history.append({
                "role": "model",
                "parts": parts
            })

            tool_responses = []
            for call in function_calls:
                tool_name = call.get("name")
                tool_args = call.get("args", {})

                print(f"[3. Tool Call Requested by LLM]:")
                print(f"    - Function : {tool_name}")
                print(f"    - Arguments: {json.dumps(tool_args)}")

                # Step 4: Execute tool locally in Python
                tool_output = execute_tool(tool_name, tool_args)

                # Record searched entity in short-term memory
                if tool_name == "document_search":
                    self.memory.set_entity(tool_args.get("query", ""))

                print(f"[4. Tool Execution Result (JSON)]:")
                print(f"    - Output: {json.dumps(tool_output)}")

                # Format tool output for Gemini v1beta format
                tool_responses.append({
                    "functionResponse": {
                        "name": tool_name,
                        "response": tool_output
                    }
                })

            # Append the tool observation to history so Gemini can read the answer
            self.history.append({
                "role": "user",
                "parts": tool_responses
            })

        return "Agent reached maximum tool call iterations."

    def reset_memory(self):
        """Clears both API conversation history and local short-term memory."""
        self.history = []
        self.memory.clear()
        print("[Memory Cleared]")
