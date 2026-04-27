# scripts/query_pipeline.py

from scripts.pageindex_query import query_tree


def query_system(user_query, doc_id, trees_cache):
    tree = trees_cache.get(doc_id)
    if not tree:
        print("\n[Error] No PageIndex tree found for the selected document.")
        return

    result = query_tree(user_query, tree)

    print("\n[Traversal]")
    for step, (node_ids, reason) in enumerate(result["traversal"], 1):
        joined = ", ".join(node_ids)
        reason_part = f" - {reason}" if reason else ""
        print(f"Step {step}: {joined}{reason_part}")

    print("\n[Answer]")
    print(result["answer"])
