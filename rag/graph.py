from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from .state import AgentState
from .retriever import retrieve_node
from .generator import generate_node

workflow = StateGraph(AgentState)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate", generate_node)

workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

bot = workflow.compile()

def run_rag(question, top_k=3):
    initial_state = {
        "question": question,
        "top_k": top_k,
        "documents": [],
        "answer": "",
        "sources": []
    }
    output = bot.invoke(initial_state)
    return {
        "answer": output.get("answer", ""),
        "sources": output.get("sources", [])
    }
