import os
import json
from typing import List
from langchain_core.documents import Document

JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data_files', 'knowledge.json')

def load_documents(path: str = JSON_PATH) -> List[Document]:
    with open(path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    return [
        Document(
            page_content=c.get('text', ''),
            metadata={'page': c.get('page'), 'title': c.get('title', '')}
        )
        for c in chunks
    ]

documents = load_documents()

def get_documents():
    return documents
