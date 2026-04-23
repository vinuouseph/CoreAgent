"""
CoreAgent-2 — File Uploader Component
Handles multimodal file uploads and ingestion into the Knowledge Vault.
"""
import streamlit as st

from core.knowledge.loaders import process_upload
from core.knowledge.vault import vault


def render_file_uploader():
    """Render the sidebar file uploader with ingestion controls."""
    st.sidebar.markdown("### Knowledge Upload")

    uploaded_files = st.sidebar.file_uploader(
        "Upload to Agent Memory",
        type=["pdf", "txt", "md", "csv", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="file_uploader",
    )

    if uploaded_files:
        # Collection name selector
        collection = st.sidebar.text_input(
            "Target Collection", value="default_knowledge", key="upload_collection"
        )

        if st.sidebar.button("Ingest to Knowledge Vault", type="primary", use_container_width=True):
            with st.sidebar.status("Processing documents...", expanded=True) as status:
                total_chunks = 0
                for file in uploaded_files:
                    try:
                        st.write(f"Reading `{file.name}` …")
                        docs = process_upload(file.getvalue(), file.name)

                        st.write(f"Ingesting {len(docs)} chunk(s) …")
                        vault.add_documents(collection, docs)
                        total_chunks += len(docs)
                    except Exception as e:
                        st.error(f"Failed: {file.name} — {e}")

                status.update(
                    label=f"Ingested {total_chunks} chunk(s)!",
                    state="complete",
                    expanded=False,
                )
            st.sidebar.success("Documents are now available for RAG!")
