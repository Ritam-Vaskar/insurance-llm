# app.py

from scripts.pageindex_index import build_pageindex_trees
from scripts.query_pipeline import query_system

def main():
    print("\n=== Insurance Document Query Assistant (Vectorless) ===\n")
    print("[1] Building PageIndex trees...")
    docs_cache, trees_cache = build_pageindex_trees()

    if not docs_cache:
        print("\n[Error] No PDF files found in data/policies.")
        return

    doc_items = list(docs_cache.items())
    selected_doc_id = None

    if len(doc_items) == 1:
        selected_doc_id = doc_items[0][1]
    else:
        print("\nAvailable documents:")
        for idx, (name, doc_id) in enumerate(doc_items, 1):
            print(f"{idx}. {name} (doc_id: {doc_id})")
        choice = input("\nSelect a document by number: ").strip()
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(doc_items):
                selected_doc_id = doc_items[index][1]

    if not selected_doc_id:
        print("\n[Error] Invalid document selection.")
        return

    # Step 2: Query loop
    print("\n[2] Ready for questions!\n")
    while True:
        query = input("\nAsk a question (or type 'exit'): ")
        if query.lower() == "exit":
            break
        query_system(query, selected_doc_id, trees_cache)

if __name__ == "__main__":
    main()
