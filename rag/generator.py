import os
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openrouter import ChatOpenRouter
from .state import AgentState, SYSTEM_PROMPT

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOTENV_PATH = os.path.join(BASE_DIR, '.env')
load_dotenv(DOTENV_PATH)

llm = ChatOpenRouter(
    model_name=os.environ.get("OPENROUTER_MODEL"),
    openrouter_api_key=os.environ.get("OPENROUTER_API_KEY"),
    temperature=0.1,
)

def generate_node(state: AgentState) -> Dict[str, Any]:
    query = state.get('question', '')
    docs = state.get('documents', [])

    if not docs:
        return {"answer": "I could not find information about that in the system brochure.", "sources": []}

    sources = [{"page": d.metadata.get('page'), "title": d.metadata.get('title')} for d in docs]
    context = "\n\n".join([f"[{d.metadata.get('title')} - Page {d.metadata.get('page')}]:\n{d.page_content}" for d in docs])

    messages = [
        SystemMessage(content=state.get('system_prompt') or SYSTEM_PROMPT),
        HumanMessage(content=f"--- BROCHURE CONTEXT ---\n{context}\n\n--- STUDENT QUESTION ---\n{query}")
    ]

    try:
        response = llm.invoke(messages)
        answer = response.content
    except Exception as e:
        answer = f"Sorry, I encountered an issue connecting to the AI assistant ({e}). Please try again."

    return {"answer": answer, "sources": sources}
