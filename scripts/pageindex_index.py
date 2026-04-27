import json
import os
import time

from dotenv import load_dotenv

from pageindex import PageIndexClient

from config import (
    DOCS_DIR,
    INDEX_DIR,
    PAGEINDEX_API_KEY_ENV,
    PAGEINDEX_DOCS_CACHE,
    PAGEINDEX_TREES_CACHE,
    PAGEINDEX_MAX_POLLS,
    PAGEINDEX_POLL_SECONDS,
)


def _load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _get_client():
    load_dotenv()
    api_key = os.getenv(PAGEINDEX_API_KEY_ENV)
    if not api_key:
        raise ValueError(
            f"Missing {PAGEINDEX_API_KEY_ENV}. Set it in your environment before running."
        )
    return PageIndexClient(api_key=api_key)


def _is_pdf_file(filename):
    return filename.lower().endswith(".pdf")


def _wait_for_tree(client, doc_id):
    for attempt in range(PAGEINDEX_MAX_POLLS):
        tree_result = client.get_tree(doc_id, node_summary=True)
        if isinstance(tree_result, dict):
            status = tree_result.get("status")
            if status == "completed":
                return tree_result.get("result", [])
            if status not in ("processing", "queued"):
                raise RuntimeError(f"Unexpected status for {doc_id}: {status}")
        elif isinstance(tree_result, list):
            return tree_result

        if attempt < PAGEINDEX_MAX_POLLS - 1:
            time.sleep(PAGEINDEX_POLL_SECONDS)

    raise TimeoutError(
        f"Timed out waiting for PageIndex tree for {doc_id} after {PAGEINDEX_MAX_POLLS} attempts."
    )


def build_pageindex_trees():
    if not os.path.isdir(DOCS_DIR):
        raise FileNotFoundError(f"Docs directory not found: {DOCS_DIR}")

    client = _get_client()
    docs_cache = _load_json(PAGEINDEX_DOCS_CACHE)
    trees_cache = _load_json(PAGEINDEX_TREES_CACHE)

    updated = False

    for filename in os.listdir(DOCS_DIR):
        if not _is_pdf_file(filename):
            continue

        file_path = os.path.join(DOCS_DIR, filename)
        doc_id = docs_cache.get(filename)

        if not doc_id:
            result = client.submit_document(file_path)
            doc_id = result.get("doc_id")
            if not doc_id:
                raise RuntimeError(f"No doc_id returned for {filename}")
            docs_cache[filename] = doc_id
            updated = True

        if doc_id not in trees_cache:
            tree = _wait_for_tree(client, doc_id)
            trees_cache[doc_id] = tree
            updated = True

    if updated:
        os.makedirs(INDEX_DIR, exist_ok=True)
        _save_json(PAGEINDEX_DOCS_CACHE, docs_cache)
        _save_json(PAGEINDEX_TREES_CACHE, trees_cache)

    return docs_cache, trees_cache
