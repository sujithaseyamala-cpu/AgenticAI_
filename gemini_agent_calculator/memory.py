"""
memory.py - Short-Term Memory and Context Buffer for Agentic AI.
Implements LangChain-style ConversationBufferWindowMemory and entity tracking without external dependencies.
"""

from typing import List, Dict, Any, Optional

class ShortTermMemory:
    """
    Manages short-term conversational memory with a sliding window buffer
    and tracked entities (e.g., student names or referenced topics).
    """

    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.turns: List[Dict[str, str]] = []  # List of {"role": "user"|"assistant", "content": "..."}
        self.last_entity: Optional[str] = None  # Tracks current subject (e.g., "Priya Sharma")

    def add_turn(self, role: str, content: str):
        """Adds a dialogue turn and maintains window size."""
        self.turns.append({"role": role, "content": content})
        if len(self.turns) > self.window_size * 2:
            self.turns = self.turns[-self.window_size * 2:]

    def set_entity(self, entity_name: str):
        """Records the latest subject/entity being discussed."""
        self.last_entity = entity_name

    def get_entity(self) -> Optional[str]:
        """Returns the active entity in short-term memory."""
        return self.last_entity

    def get_history_messages(self) -> List[Dict[str, Any]]:
        """Returns turns in standard message format."""
        return self.turns

    def get_summary(self) -> str:
        """Returns a string representation of the short-term memory buffer."""
        if not self.turns:
            return "No previous memory."
        lines = []
        for turn in self.turns[-6:]:
            lines.append(f"{turn['role'].capitalize()}: {turn['content']}")
        return "\n".join(lines)

    def clear(self):
        """Clears the short-term memory buffer."""
        self.turns = []
        self.last_entity = None
