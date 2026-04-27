# scripts/query_pipeline.py

import os
import pickle
from scripts.bm25 import tokenize
from config import INDEX_DIR
from llm.generate_answer import ask_llm

def query_system(user_query):
    index_path = os.path.join(INDEX_DIR, "bm25_index.pkl")
    docs_path = os.path.join(INDEX_DIR, "docs.pkl")
    
    if not os.path.exists(index_path) or not os.path.exists(docs_path):
        print(f"\n[Error] No index found. Please run the document parsing and indexing steps first.")
        return

    with open(index_path, "rb") as f:
        bm25 = pickle.load(f)
    
    with open(docs_path, "rb") as f:
        docs = pickle.load(f)

    tokenized_query = tokenize(user_query)
    scores = bm25.get_scores(tokenized_query)
    
    # Get top 3 paragraphs
    top_n = 3
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_n]
    
    top_paragraphs = [docs[i]["text"] for i in top_indices if scores[i] > 0]
    
    if not top_paragraphs:
        print("\n[No Context] No relevant context found.")
        return

    print("\n[Context Retrieved]")
    for i, idx in enumerate(top_indices[:len(top_paragraphs)], 1):
        doc = docs[idx]
        print(f"{i}. [Page {doc['page_num']} of {doc['doc_id']}] {doc['text'][:150]}...")

    print("\n[Answer]")
    response = ask_llm(user_query, top_paragraphs)
    print(response)
