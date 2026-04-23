"""
CoreAgent-2 — Knowledge Vault (ChromaDB Wrapper)
Provides CRUD + semantic search over persistent vector collections.
"""
import chromadb
from langchain_core.documents import Document

from core.config import config
from core.knowledge.embeddings import get_embeddings


class KnowledgeVault:
    """Production-grade ChromaDB wrapper with embedding-aware search."""

    def __init__(self):
        self.client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)
        self.embeddings = get_embeddings()

    # ── Collection CRUD ──────────────────────────────────────────────────

    def get_or_create_collection(self, name: str, metadata: dict | None = None):
        return self.client.get_or_create_collection(name=name, metadata=metadata)

    def list_collections(self) -> list[str]:
        """Return a simple list of collection name strings."""
        raw = self.client.list_collections()
        # ChromaDB may return Collection objects or plain strings depending on version
        if raw and not isinstance(raw[0], str):
            return [c.name for c in raw]
        return list(raw)

    def get_collection_info(self, name: str) -> dict:
        try:
            col = self.client.get_collection(name=name)
            return {
                "name": col.name,
                "count": col.count(),
                "metadata": col.metadata,
            }
        except Exception as e:
            return {"error": str(e)}

    # ── Document Ingestion ───────────────────────────────────────────────

    def add_documents(self, collection_name: str, docs: list[Document]):
        col = self.get_or_create_collection(collection_name)

        texts = [doc.page_content for doc in docs]
        metadatas = [doc.metadata for doc in docs]
        ids = [f"{collection_name}_{i}_{abs(hash(t))}" for i, t in enumerate(texts)]

        embeddings_list = self.embeddings.embed_documents(texts)
        col.add(documents=texts, metadatas=metadatas, ids=ids, embeddings=embeddings_list)

    # ── Semantic Search ──────────────────────────────────────────────────

    def search(
        self,
        query: str,
        collection_name: str | None = None,
        top_k: int | None = None,
        threshold: float | None = None,
    ) -> list[Document]:
        top_k = top_k or config.TOP_K_RESULTS
        threshold = threshold or config.SIMILARITY_THRESHOLD
        col_name = collection_name or "default_knowledge"

        try:
            col = self.client.get_collection(col_name)
        except Exception:
            return []

        query_embedding = self.embeddings.embed_query(query)
        results = col.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        documents: list[Document] = []
        if not results["documents"]:
            return documents

        for i in range(len(results["documents"][0])):
            distance = results["distances"][0][i]
            if distance <= threshold:
                doc = Document(
                    page_content=results["documents"][0][i],
                    metadata=results["metadatas"][0][i],
                )
                doc.metadata["distance"] = round(distance, 4)
                documents.append(doc)

        return documents

    # ── Deletion ─────────────────────────────────────────────────────────

    def delete_documents(self, collection_name: str, ids: list[str]) -> bool:
        try:
            col = self.client.get_collection(collection_name)
            col.delete(ids=ids)
            return True
        except Exception:
            return False

    def delete_collection(self, name: str) -> bool:
        try:
            self.client.delete_collection(name=name)
            return True
        except Exception:
            return False


# Global singleton
vault = KnowledgeVault()
