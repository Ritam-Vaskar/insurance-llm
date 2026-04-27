# app.py

from scripts import parse_documents, build_index, query_pipeline

def main():
    print("\n=== Insurance Document Query Assistant (Vectorless) ===\n")
    
    # Step 1: Parse docs (only if not already parsed)
    print("[1] Parsing documents into pages...")
    parse_documents.parse_all()

    # Step 2: Build page index
    print("[2] Building BM25 index...")
    build_index.build_bm25_index()

    # Step 3: Query loop
    print("\n[3] Ready for questions!\n")
    while True:
        query = input("\n🧠 Ask a question (or type 'exit'): ")
        if query.lower() == "exit":
            break
        query_pipeline.query_system(query)

if __name__ == "__main__":
    main()
