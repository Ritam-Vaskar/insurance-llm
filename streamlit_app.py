import streamlit as st

from scripts.pageindex_index import build_pageindex_trees
from scripts.pageindex_query import query_tree


st.set_page_config(page_title="Insurance QA (PageIndex)", layout="wide")

st.title("Insurance Policy QA (PageIndex, Vectorless)")
st.caption("Tree-based retrieval with Groq reasoning.")

if "docs_cache" not in st.session_state:
    st.session_state.docs_cache = {}
if "trees_cache" not in st.session_state:
    st.session_state.trees_cache = {}

with st.sidebar:
    st.header("Indexing")
    if st.button("Build/Refresh PageIndex Trees", use_container_width=True):
        with st.spinner("Building PageIndex trees..."):
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

            st.subheader("Answer")
            st.write(result["answer"])

            st.subheader("Retrieval Log")
            traversal_lines = []
            for step, (node_ids, reason) in enumerate(result["traversal"], 1):
                reason_part = f" | reason: {reason}" if reason else ""
                traversal_lines.append(f"Step {step}: {', '.join(node_ids)}{reason_part}")
            st.code("\n".join(traversal_lines) or "No traversal steps recorded.")

            st.subheader("Selected Nodes")
            for node in result["selected_nodes"]:
                page_info = "pages unknown"
                if node["start_page"] is not None and node["end_page"] is not None:
                    page_info = f"pages {node['start_page']}-{node['end_page']}"
                with st.expander(f"{node['title']} ({node['node_id']}, {page_info})"):
                    st.write(node["context"])
