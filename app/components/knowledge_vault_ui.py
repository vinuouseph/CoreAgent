"""
CoreAgent-2 — Knowledge Vault UI Component
Browse, Search, and Manage ChromaDB collections.
"""
import streamlit as st
import pandas as pd

from core.knowledge.vault import vault
from core.knowledge.loaders import process_upload


def render_knowledge_vault_ui():
    """Full Knowledge Vault management panel with Browse/Search/Manage tabs."""
    st.header("Knowledge Vault")
    st.markdown("<br>", unsafe_allow_html=True)

    tabs = st.tabs(["Browse Collections", "Search Playground", "Manage"])

    # ── Browse ───────────────────────────────────────────────────────────
    with tabs[0]:
        st.subheader("Existing Collections")
        try:
            collections = vault.list_collections()
            if collections:
                data = []
                for col_name in collections:
                    info = vault.get_collection_info(col_name)
                    data.append({
                        "Collection": col_name,
                        "Chunks": info.get("count", 0),
                        "Metadata": str(info.get("metadata", {})),
                    })
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True, hide_index=True)

                # Peek into a collection
                st.markdown("<br>", unsafe_allow_html=True)
                selected = st.selectbox("Inspect Collection", options=collections, key="browse_col")
                if st.button("Show Sample Documents", key="peek_btn"):
                    try:
                        col = vault.client.get_collection(selected)
                        sample = col.peek(limit=5)
                        if sample and sample.get("documents"):
                            for i, doc in enumerate(sample["documents"]):
                                with st.expander(f"Document {i+1}", expanded=False):
                                    st.write(doc[:500] + "…" if len(doc) > 500 else doc)
                                    if sample.get("metadatas"):
                                        st.json(sample["metadatas"][i])
                        else:
                            st.info("Collection is empty.")
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.info("No collections found. Upload documents to get started!")
        except Exception as e:
            st.error(f"ChromaDB connection error: {e}")

    # ── Search ───────────────────────────────────────────────────────────
    with tabs[1]:
        st.subheader("Semantic Search Playground")

        col1, col2 = st.columns([3, 1])
        with col1:
            query = st.text_input("Enter search query:", key="search_query")
        with col2:
            try:
                col_names = vault.list_collections() or ["default_knowledge"]
            except Exception:
                col_names = ["default_knowledge"]
            selected_col = st.selectbox("Collection", options=col_names, key="search_col")

        c1, c2 = st.columns(2)
        with c1:
            top_k = st.slider("Top K Results", 1, 10, 3, key="search_top_k")
        with c2:
            threshold = st.slider("Distance Threshold", 0.1, 2.0, 1.2, 0.1, key="search_threshold")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Search", key="search_btn", type="primary"):
            if query:
                with st.spinner("Searching…"):
                    results = vault.search(query, selected_col, top_k, threshold)
                    if results:
                        st.success(f"Found {len(results)} result(s)")
                        for i, doc in enumerate(results):
                            distance = doc.metadata.get("distance", "N/A")
                            with st.expander(f"Result {i+1} — Distance: {distance:.4f}" if isinstance(distance, float) else f"Result {i+1}"):
                                st.markdown(doc.page_content)
                                st.json(doc.metadata)
                    else:
                        st.warning("No results within the threshold.")
            else:
                st.warning("Enter a query first.")

    # ── Manage ───────────────────────────────────────────────────────────
    with tabs[2]:
        st.subheader("Database Management")

        # Upload to specific collection
        st.markdown("**Upload Documents**")
        mgmt_files = st.file_uploader(
            "Select files",
            type=["pdf", "txt", "md", "csv", "png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key="mgmt_uploader",
        )
        mgmt_collection = st.text_input("Target Collection", value="default_knowledge", key="mgmt_col")

        st.markdown("<br>", unsafe_allow_html=True)
        if mgmt_files and st.button("Ingest", key="mgmt_ingest", type="primary"):
            with st.spinner("Processing…"):
                for f in mgmt_files:
                    try:
                        docs = process_upload(f.getvalue(), f.name)
                        vault.add_documents(mgmt_collection, docs)
                        st.success(f"`{f.name}` → {len(docs)} chunks")
                    except Exception as e:
                        st.error(f"`{f.name}`: {e}")

        st.divider()

        # Delete collection
        st.markdown("**Delete Collection**")
        del_col = st.text_input("Collection name to delete:", key="del_col")
        if st.button("Delete Collection", key="del_btn"):
            if del_col:
                if vault.delete_collection(del_col):
                    st.success(f"Deleted `{del_col}`.")
                    st.rerun()
                else:
                    st.error(f"Failed to delete `{del_col}`.")
