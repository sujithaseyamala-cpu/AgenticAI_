"""
main.py - Interactive CLI runner to practice with your Agentic AI Calculator.
No extra frameworks. Pure Python.
"""

import os
import sys
from agent import BasicCalculatorAgent

def get_api_key() -> str:
    """
    Finds the Gemini API Key from quickstart.py, environment variables, or asks the user.
    """
    # 1. Check quickstart.py if previously saved
    try:
        from quickstart import GEMINI_API_KEY
        if GEMINI_API_KEY and GEMINI_API_KEY.strip():
            return GEMINI_API_KEY.strip()
    except Exception:
        pass

    # 2. Check environment variable
    env_key = os.getenv("GEMINI_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    # 3. Check .env file
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")

    # 4. Fallback prompt
    print("\n[Gemini API Key Required]")
    key = input("Paste your Gemini API Key: ").strip()
    if not key:
        print("API key is required to proceed.")
        sys.exit(1)
    return key


def main():
    print("=" * 70)
    print("   AGENTIC AI: RAG STUDENT DATABASE + MEMORY + TOOLS   ")
    print("=" * 70)

    api_key = get_api_key()
    agent = BasicCalculatorAgent(api_key=api_key)

    print("\nAgent initialized with 4 tools: ['document_search', 'calculator', 'web_search', 'get_current_datetime']")
    print("Commands: 'reset' (clear memory), 'memory' (view memory), 'exit' (quit)")
    print("\nTry Document Search & RAG questions from your uploaded PDF:")
    print("  1. 'What is Priya Sharma's attendance and overall mark?'")
    print("  2. 'Who has the highest overall mark?'")
    print("  3. 'Which students belong to the CSE department?'")
    print("  4. 'List students whose attendance is below 75%.'")
    print("  5. 'Who scored above 90 in AI?'")
    print("  6. 'How many students are placement eligible?'")
    print("  7. 'What is Arjun Kumar's DSA mark?'")
    print("  8. 'Which student has the highest attendance?'")
    print("  9. 'Find all AIDS students with an overall mark above 80.'")
    print("  10. 'What is the phone number of Fathima N?'")
    print("  11. Short-Term Memory test: Follow up with 'What is her email?'")
    print("-" * 70)

    while True:
        try:
            user_input = input("\nYou > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Exiting agent session. Happy practicing!")
                break
            if user_input.lower() == "reset":
                agent.reset_memory()
                continue
            if user_input.lower() == "memory":
                print(f"\n[Short-Term Memory Buffer]:\n{agent.memory.get_summary()}\n")
                continue

            # Execute the agent
            answer = agent.run(user_input)
            print(f"\nAgent Answer:\n{answer}")

        except (KeyboardInterrupt, EOFError):
            print("\nSession stopped.")
            break
        except Exception as e:
            print(f"\n[Error]: {e}")


if __name__ == "__main__":
    main()
