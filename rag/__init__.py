from .graph import run_rag, bot
from .loader import get_documents
from .retriever import find_relevant_documents

def ask(query: str, top_k: int = 3):
    return run_rag(query, top_k=top_k)

__all__ = ["ask", "run_rag", "bot", "get_documents", "find_relevant_documents"]
