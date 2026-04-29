# scripts/query_pipeline.py

from scripts.pageindex_query import query_tree


def query_system(user_query, doc_id, trees_cache):
    tree = trees_cache.get(doc_id)
    if not tree:
        raise ValueError("No PageIndex tree found for the selected document. Please rebuild the index.")

    result = query_tree(user_query, tree)

    return {
        "answer": result["answer"],
        "traversal": result["traversal"]
    }
