# scripts/build_index.py

import json
import pickle
import os
from scripts.bm25 import BM25, tokenize
from config import INDEX_DIR

def build_bm25_index():
    with open("chunks/chunked_docs.json", "r", encoding="utf-8") as f:
        docs = json.load(f)
        
    corpus = [tokenize(doc["text"]) for doc in docs]
    bm25 = BM25(corpus)
    
    os.makedirs(INDEX_DIR, exist_ok=True)
    
    # Save the index and documents
    with open(os.path.join(INDEX_DIR, "bm25_index.pkl"), "wb") as f:
        pickle.dump(bm25, f)
        
    with open(os.path.join(INDEX_DIR, "docs.pkl"), "wb") as f:
        pickle.dump(docs, f)

