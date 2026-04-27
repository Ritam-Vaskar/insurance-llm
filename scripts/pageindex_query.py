import json

from llm.gemini_client import generate_text
from config import (
    NODE_TEXT_MAX_CHARS,
    TREE_MAX_DEPTH,
    TREE_MAX_NODES_PER_STEP,
    TREE_SELECT_TOP_K,
)


def _extract_json_object(text):
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


def _get_page_range(node):
    start = node.get("start_index") or node.get("page_index")
    end = node.get("end_index") or node.get("page_index")
    if start is None and "page" in node:
        start = node.get("page")
        end = node.get("page")
    return start, end


def _shorten_text(text, limit):
    if not text:
        return ""
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def _node_summary(node):
    return (
        node.get("summary")
        or node.get("node_summary")
        or _shorten_text(node.get("text") or "", 400)
    )


def _normalize_node_id(node_id, fallback):
    if node_id is None or str(node_id).strip() == "":
        return fallback
    return str(node_id)


def _build_maps(tree):
    node_map = {}
    children_map = {}
    root_ids = []

    def walk(nodes, path_prefix):
        for idx, node in enumerate(nodes):
            fallback_id = f"node-{path_prefix}-{idx}"
            node_id = _normalize_node_id(node.get("node_id"), fallback_id)
            node["_node_id"] = node_id
            node_map[node_id] = node

            children = node.get("nodes") or []
            children_ids = []
            for child_index, child in enumerate(children):
                child_fallback = f"node-{path_prefix}-{idx}-{child_index}"
                child_id = _normalize_node_id(child.get("node_id"), child_fallback)
                children_ids.append(child_id)
            children_map[node_id] = children_ids

            if path_prefix == "root":
                root_ids.append(node_id)

            walk(children, f"{path_prefix}-{idx}")

    walk(tree, "root")
    return node_map, children_map, root_ids


def _format_candidate_nodes(node_ids, node_map):
    lines = []
    for node_id in node_ids[:TREE_MAX_NODES_PER_STEP]:
        node = node_map[node_id]
        start, end = _get_page_range(node)
        summary = _node_summary(node)
        if start is not None and end is not None:
            page_part = f"pages {start}-{end}"
        else:
            page_part = "pages unknown"
        lines.append(
            f"- id: {node_id}; title: {node.get('title', '')}; {page_part}; summary: {summary}"
        )
    return "\n".join(lines)


def _select_nodes_with_llm(question, node_ids, node_map, depth):
    candidates_text = _format_candidate_nodes(node_ids, node_map)

    prompt = f"""You are selecting the most relevant sections in a document tree.
Question: {question}

Candidates:
{candidates_text}

Rules:
- Pick up to {TREE_SELECT_TOP_K} node ids that best match the question.
- Prefer precise sections over broad ones.
- If none look relevant, return an empty list.

Return JSON only:
{{"selected_ids": ["id1", "id2"], "reason": "...", "drill_down": true}}
"""

    raw = generate_text(prompt, temperature=0.1)
    data = _extract_json_object(raw) or {}
    selected = data.get("selected_ids") or []
    selected = [sid for sid in selected if sid in node_map]
    drill_down = bool(data.get("drill_down"))

    if not selected:
        fallback = node_ids[:TREE_SELECT_TOP_K]
        return fallback, "fallback", False

    return selected, data.get("reason") or "", drill_down


def _collect_context(selected_ids, node_map):
    contexts = []
    for node_id in selected_ids:
        node = node_map[node_id]
        start, end = _get_page_range(node)
        text = node.get("text") or ""
        summary = _node_summary(node)
        context_text = _shorten_text(text or summary, NODE_TEXT_MAX_CHARS)
        contexts.append(
            {
                "node_id": node_id,
                "title": node.get("title", ""),
                "start_page": start,
                "end_page": end,
                "context": context_text,
            }
        )
    return contexts


def _answer_with_reasons(question, contexts):
    context_lines = []
    for ctx in contexts:
        page_info = "pages unknown"
        if ctx["start_page"] is not None and ctx["end_page"] is not None:
            page_info = f"pages {ctx['start_page']}-{ctx['end_page']}"
        context_lines.append(
            f"Node {ctx['node_id']} ({ctx['title']}, {page_info}): {ctx['context']}"
        )

    prompt = f"""You are an insurance policy assistant.
Use ONLY the context below.
Question: {question}

Context:
""" + "\n".join(context_lines) + """

Provide a detailed answer with reasons.
Format:
Answer: <final answer>
Reasons:
1) <reason with node title/page>
2) <reason with node title/page>
If the context is insufficient, say what is missing.
"""

    return generate_text(prompt, temperature=0.2)


def query_tree(question, tree):
    node_map, children_map, root_ids = _build_maps(tree)

    current_ids = root_ids
    selected_ids = []
    traversal = []

    for depth in range(TREE_MAX_DEPTH):
        if not current_ids:
            break

        selected, reason, drill_down = _select_nodes_with_llm(
            question, current_ids, node_map, depth
        )
        selected_ids = selected
        traversal.append((selected, reason))

        if not drill_down:
            break

        next_ids = []
        for node_id in selected:
            next_ids.extend(children_map.get(node_id, []))
        current_ids = next_ids

    contexts = _collect_context(selected_ids, node_map)
    answer = _answer_with_reasons(question, contexts)

    return {
        "answer": answer,
        "selected_nodes": contexts,
        "traversal": traversal,
    }
