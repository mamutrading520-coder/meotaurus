"""Docs services package.

Exports are lazy so importing lightweight management tools does not
eagerly initialize RAG/vector dependencies.
"""

__all__ = [
    "DocsService",
    "DocChunk",
    "IndexResult",
    "RAGManager",
    "VectorRAG",
    "do_manage_documents",
]


def __getattr__(name):
    if name in {"DocsService", "DocChunk", "IndexResult"}:
        from .service import DocsService, DocChunk, IndexResult

        return {
            "DocsService": DocsService,
            "DocChunk": DocChunk,
            "IndexResult": IndexResult,
        }[name]

    if name == "RAGManager":
        from src.rag_manager import RAGManager

        return RAGManager

    if name == "VectorRAG":
        from src.rag_vector import VectorRAG

        return VectorRAG

    if name == "do_manage_documents":
        from .management_service import do_manage_documents

        return do_manage_documents

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
