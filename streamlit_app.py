import streamlit as st
import os
from scripts.parse_documents import parse_documents
from scripts.build_index import build_index
from scripts.pageindex_index import build_pageindex_trees
from scripts.pageindex_query import query_tree


def _page_range(node):
    start = node.get("start_index") or node.get("page_index")
    end = node.get("end_index") or node.get("page_index")
    if start is None and "page" in node:
        start = node.get("page")
        end = node.get("page")
    return start, end


def _render_tree(nodes, selected_ids, depth=0, max_depth=8):
    if depth >= max_depth:
        return
    for node in nodes:
        node_id = str(node.get("node_id") or "")
        title = node.get("title") or "(untitled)"
        start, end = _page_range(node)
        page_info = "pages ?"
        if start is not None and end is not None:
            page_info = f"pages {start}-{end}"
        selected_tag = " **[selected]**" if node_id in selected_ids else ""
        indent = "  " * depth
        st.markdown(f"{indent}- {title} ({node_id}, {page_info}){selected_tag}")
        children = node.get("nodes") or []
        if children:
            _render_tree(children, selected_ids, depth + 1, max_depth=max_depth)


st.set_page_config(page_title="Insurance QA (PageIndex)", layout="wide")

st.title("Insurance Policy QA (PageIndex, Vectorless)")
st.caption("Tree-based retrieval with Groq reasoning.")

if "docs_cache" not in st.session_state:
    st.session_state.docs_cache = {}
if "trees_cache" not in st.session_state:
    st.session_state.trees_cache = {}

# Add file uploader for user-uploaded PDFs
uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

if uploaded_files:
    st.info("Processing uploaded files...")
    for uploaded_file in uploaded_files:
        file_path = os.path.join("data/policies", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
    st.success("Files uploaded successfully. Click 'Build/Refresh PageIndex Trees' to index them.")

with st.sidebar:
    st.header("Indexing")
    if st.button("Build/Refresh PageIndex Trees", use_container_width=True):
        with st.spinner("Building PageIndex trees..."):
            parse_documents("data/policies")  # Parse all documents in the folder
            build_index("data/policies")  # Build index for parsed documents
            docs_cache, trees_cache = build_pageindex_trees()
            st.session_state.docs_cache = docs_cache
            st.session_state.trees_cache = trees_cache
        st.success("Index ready.")

    if not st.session_state.docs_cache:
        st.info("Add PDF files to data/policies and click Build.")

    doc_items = list(st.session_state.docs_cache.items())
    doc_label_map = {f"{name} (doc_id: {doc_id})": doc_id for name, doc_id in doc_items}
    doc_labels = list(doc_label_map.keys())

    selected_label = None
    if doc_labels:
        selected_label = st.selectbox("Select document", doc_labels)

question = st.text_input("Ask a question about the policy")
ask = st.button("Ask", type="primary", use_container_width=True)

if ask:
    if not st.session_state.docs_cache or not st.session_state.trees_cache:
        st.error("No index loaded. Build PageIndex trees first.")
    elif not selected_label:
        st.error("Select a document first.")
    elif not question.strip():
        st.error("Enter a question to continue.")
    else:
        doc_id = doc_label_map[selected_label]
        tree = st.session_state.trees_cache.get(doc_id)
        if not tree:
            st.error("No tree found for the selected document. Rebuild the index.")
        else:
            with st.spinner("Retrieving nodes and generating answer..."):
                result = query_tree(question, tree)

            all_selected_ids = []
            for node_ids, _reason in result["traversal"]:
                all_selected_ids.extend(node_ids)
            selected_id_set = set(all_selected_ids)

            answer_tab, log_tab, nodes_tab, tree_tab = st.tabs(
                ["Answer", "Retrieval Log", "Selected Nodes", "Tree Structure"]
            )

            with answer_tab:
                st.subheader("Answer")
                st.write(result["answer"])

            with log_tab:
                st.subheader("Retrieval Log")
                traversal_lines = []
                for step, (node_ids, reason) in enumerate(result["traversal"], 1):
                    reason_part = f" | reason: {reason}" if reason else ""
                    traversal_lines.append(
                        f"Step {step}: {', '.join(node_ids)}{reason_part}"
                    )
                st.code("\n".join(traversal_lines) or "No traversal steps recorded.")

            with nodes_tab:
                st.subheader("Selected Nodes (All Steps)")
                if not result["selected_nodes"]:
                    st.info("No selected nodes returned.")
                for node in result["selected_nodes"]:
                    page_info = "pages unknown"
                    if node["start_page"] is not None and node["end_page"] is not None:
                        page_info = f"pages {node['start_page']}-{node['end_page']}"
                    with st.expander(
                        f"{node['title']} ({node['node_id']}, {page_info})"
                    ):
                        st.write(node["context"])

            with tree_tab:
                st.subheader("Tree Structure (Selected Highlighted)")
                if not tree:
                    st.info("No tree available.")
                else:
                    _render_tree(tree, selected_id_set)
