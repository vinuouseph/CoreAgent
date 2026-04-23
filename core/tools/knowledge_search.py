"""
CoreAgent-2 — Knowledge Search Tool
LangChain @tool wrapping the Knowledge Vault semantic search.
"""
from langchain_core.tools import tool
from core.knowledge.vault import vault


@tool
def knowledge_search(query: str, collection_name: str = None) -> str:
    """
    Search the internal knowledge base for information.
    Use this when the user asks a question that might be answered by uploaded documents.
    """
    try:
        docs = vault.search(query=query, collection_name=collection_name)
        if not docs:
            return "No relevant information found in the knowledge base."
        return "\n\n".join(
            f"Document [{doc.metadata.get('source', 'Unknown')}]:\n{doc.page_content}" for doc in docs
        )
    except Exception as e:
        return f"Error searching knowledge base: {e}"
