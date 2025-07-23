# app.py

from scripts import parse_documents, embed_and_store, query_pipeline

def main():
    print("\n=== Insurance Document Query Assistant ===\n")
    
    # Step 1: Parse docs (only if not already parsed)
    print("[1] Parsing documents...")
    parse_documents.parse_all()

    # Step 2: Embed and store (only if not already embedded)
    print("[2] Embedding and storing chunks into ChromaDB...")
    embed_and_store.embed_chunks()

    # Step 3: Query loop
    print("\n[3] Ready for questions!\n")
    while True:
        query = input("\n🧠 Ask a question (or type 'exit'): ")
        if query.lower() == "exit":
            break
        query_pipeline.query_system(query)

if __name__ == "__main__":
    main()
