# scripts/embed_and_store.py

import json
import chromadb
from models.huggingface_model import load_embedding_model
from config import VECTOR_DB_DIR, COLLECTION_NAME

def embed_chunks():
    # Use PersistentClient instead of Client for automatic persistence
    client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
    collection = client.get_or_create_collection(COLLECTION_NAME)
    model = load_embedding_model()

    with open("chunks/chunked_docs.json") as f:
        docs = json.load(f)

    for chunk in docs:
        embedding = model.encode(chunk["text"])
        collection.add(
            documents=[chunk["text"]],
            embeddings=[embedding.tolist()],
            metadatas=[{
                "doc_id": chunk["doc_id"],
                "index": chunk["index"]
            }],
            ids=[f"{chunk['doc_id']}_{chunk['index']}"]
        )

    # No need to call persist() with PersistentClient
    pass
