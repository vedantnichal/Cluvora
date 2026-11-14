import os
import json
import re
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.embeddings import Embeddings
from .loader import get_documents
from .state import AgentState

def get_embeddings_adapter():
    try:
        from fastembed import TextEmbedding
        embedder = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
        return type(
            'FastEmbedAdapter',
            (Embeddings,),
            {
                'embed_documents': lambda self, texts: [v.tolist() for v in embedder.embed(texts)],
                'embed_query': lambda self, text: list(embedder.embed([text]))[0].tolist()
            }
        )()
    except Exception as e:
        print(f"Fastembed unavailable ({e}).")
        return None

def build_vectorstore():
    embeddings = get_embeddings_adapter()
    store = InMemoryVectorStore(embedding=embeddings)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, 'data_files')
    json_path = os.path.join(data_dir, 'knowledge.json') if os.path.exists(os.path.join(data_dir, 'knowledge.json')) else os.path.join(current_dir, 'knowledge.json')
    emb_path = os.path.join(data_dir, 'embeddings.json') if os.path.exists(os.path.join(data_dir, 'embeddings.json')) else os.path.join(current_dir, 'embeddings.json')

    if os.path.exists(json_path) and os.path.exists(emb_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        with open(emb_path, 'r', encoding='utf-8') as f:
            emb_data = json.load(f)

        for i, (chunk, emb) in enumerate(zip(chunks, emb_data)):
            doc_id = f"chunk_{i}_p{chunk.get('page')}"
            store.store[doc_id] = {
                'id': doc_id,
                'vector': emb['embedding'],
                'text': chunk['text'],
                'metadata': {'page': chunk['page'], 'title': chunk['title']}
            }
    else:
        docs = get_documents()
        if docs:
            store.add_documents(docs)

    return store

vectorstore = build_vectorstore()
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 4, "fetch_k": min(20, max(1, len(vectorstore.store)))}
)

def find_relevant_documents(query, top_k=2):
    if not vectorstore.store:
        return []
    docs = retriever.invoke(query)
    return docs[:top_k]

def retrieve_node(state):
    query = state.get('question', '')
    top_k = state.get('top_k', 2)
    docs = find_relevant_documents(query, top_k=top_k)
    return {"documents": docs}
