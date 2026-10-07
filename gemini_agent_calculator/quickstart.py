"""
Quickstart Runner for Gemini Calculator Agent.
Shows how to configure and pass the API Key directly in Python.
"""

import os
from agent import GeminiCalculatorAgent

# ==============================================================================
# 🔑 OPTION A: Hardcode your API key below for testing:
# ==============================================================================
GEMINI_API_KEY = "AQ.Ab8RN6JTKJcJ5M4hBgDtvaYHcKxPh8fq7B2NLaJxuYw70iUgyA"  # <-- Paste your Google AI Studio key here (e.g. "AIzaSy...")

# ==============================================================================
# 🔑 OPTION B: Or read from environment variable / interactive fallback
# ==============================================================================
def get_api_key() -> str:
    # 1. Use hardcoded variable if provided above
    if GEMINI_API_KEY and GEMINI_API_KEY.strip() != "":
        return GEMINI_API_KEY.strip()

    # 2. Check system environment variable
    env_key = os.getenv("GEMINI_API_KEY")
    if env_key:
        return env_key.strip()

    # 3. Check local .env file (if present)
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("GEMINI_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")

    # 4. Interactive fallback prompt
    print("\n[API Key Required]")
    user_key = input("Enter your Gemini API Key: ").strip()
    if not user_key:
        raise ValueError("No API key provided. Cannot proceed.")
    return user_key


if __name__ == "__main__":
    # Retrieve the key
    api_key = get_api_key()

    print("\nInitializing Gemini Calculator Agent...")
    agent = GeminiCalculatorAgent(api_key=api_key, verbose=True)

    # Example 1: Arithmetic expression
    print("\n--- Example 1: Complex Arithmetic ---")
    query1 = "What is (125 * 40) + (960 / 8) - (3 ** 4)?"
    result1 = agent.chat(query1)
    print("\nFinal Answer:\n", result1)

    # Example 2: Word problem
    print("\n--- Example 2: Financial Word Problem ---")
    query2 = "An investor starts with $50,000. They earn 18% in year one, pay a 15% capital gains tax on that profit, then split the remaining profit among 3 accounts. How much profit goes to each account?"
    result2 = agent.chat(query2)
    print("\nFinal Answer:\n", result2)
