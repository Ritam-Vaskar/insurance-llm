# scripts/query_pipeline.py

import chromadb
from models.huggingface_model import load_embedding_model
from config import VECTOR_DB_DIR, COLLECTION_NAME
from llm.generate_answer import ask_llm

def query_system(user_query):
    try:
        # Use PersistentClient for consistency with storage
        client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
        collection = client.get_collection(COLLECTION_NAME)
    except chromadb.errors.NotFoundError:
        print(f"\n❌ Error: No document collection found. Please run the document processing and embedding steps first.")
        return
    model = load_embedding_model()

    embedding = model.encode(user_query)

    results = collection.query(
        query_embeddings=[embedding.tolist()],
        n_results=5
    )

    top_paragraphs = results['documents'][0]
    print("\n🔍 Context Retrieved:")
    for i, para in enumerate(top_paragraphs, 1):
        print(f"{i}. {para[:200]}...")

    print("\n🤖 Answer:")
    response = ask_llm(user_query, top_paragraphs)
    print(response)
