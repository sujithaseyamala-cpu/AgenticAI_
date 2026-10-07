"""
langchain_student_rag.py - Reference implementation using LangChain concepts.
Demonstrates:
  1. Document creation from the uploaded Student Database.
  2. RAG Retrieval Tool.
  3. Short-Term Memory (ConversationBufferWindowMemory).
  4. LangChain Agent workflow.
"""

from typing import List, Dict, Any
from student_data import STUDENTS_DATABASE

# ==============================================================================
# 1. RAG DOCUMENTS (LangChain Document Structure)
# Each student record is formatted into a Document chunk with metadata.
# ==============================================================================
class StudentDocument:
    def __init__(self, page_content: str, metadata: Dict[str, Any]):
        self.page_content = page_content
        self.metadata = metadata

def build_student_documents() -> List[StudentDocument]:
    docs = []
    for s in STUDENTS_DATABASE:
        content = (
            f"Student ID: {s['student_id']}\n"
            f"Name: {s['name']}\n"
            f"Department: {s['dept']}\n"
            f"Year: {s['year']}\n"
            f"Email: {s['email']}\n"
            f"Phone: {s['phone']}\n"
            f"Attendance: {s['attendance']}%\n"
            f"Python: {s['python']}\n"
            f"DSA: {s['dsa']}\n"
            f"AI: {s['ai']}\n"
            f"Overall: {s['overall']}\n"
            f"Placement Status: {s['placement']}"
        )
        docs.append(StudentDocument(page_content=content, metadata=s))
    return docs


# ==============================================================================
# 2. SHORT-TERM MEMORY (LangChain ConversationBufferWindowMemory Concept)
# Keeps a sliding window of the last k conversation turns.
# ==============================================================================
class LangChainStyleBufferMemory:
    """Simulates LangChain's ConversationBufferWindowMemory(k=5)."""
    def __init__(self, k: int = 5):
        self.k = k
        self.history = []

    def save_context(self, user_input: str, ai_output: str):
        self.history.append({"input": user_input, "output": ai_output})
        if len(self.history) > self.k:
            self.history = self.history[-self.k:]

    def load_memory_variables(self) -> Dict[str, str]:
        buffer_str = ""
        for turn in self.history:
            buffer_str += f"Human: {turn['input']}\nAI: {turn['output']}\n"
        return {"chat_history": buffer_str}


if __name__ == "__main__":
    docs = build_student_documents()
    print(f"Loaded {len(docs)} student documents for RAG.")
    print("\nSample Document Chunk:\n")
    print(docs[1].page_content)  # Priya Sharma
    
    memory = LangChainStyleBufferMemory(k=3)
    memory.save_context("What is Priya Sharma's attendance?", "Priya Sharma's attendance is 92%.")
    print("\nShort-Term Memory Buffer:\n", memory.load_memory_variables()["chat_history"])
