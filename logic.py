"""Simple chatbot integration using LlamaIndex over Places & Reviews.

This module builds a textual corpus from the `Place` and `Review` models
and uses `llama_index` (if installed) to create an in-memory vector
index. The index is cached in-module to avoid rebuilding on every
query. The implementation is intentionally minimal — in production you
would persist the index, handle rate limits and protect API keys.
"""

from typing import List
from api.models import Place, Review

# Optional LlamaIndex imports - we wrap in try/except to provide
# a clear error message if the dependency is missing.
try:
    from llama_index import Document
    from llama_index.core import VectorStoreIndex
except Exception as e:
    VectorStoreIndex = None  # type: ignore


_CACHED_INDEX = None


def build_corpus_from_db() -> List["Document"]:
    """Build a list of textual documents from Places and Reviews.

    Returns a list of `llama_index.Document` objects (if available).
    """
    if VectorStoreIndex is None:
        raise RuntimeError("llama_index is not installed. Install it to enable chatbot features.")

    documents = []

    # --- Places ---
    for p in Place.objects.all():
        txt = (
            f"PLACE:\nName: {p.name}\nNeighborhood: {p.neighborhood}\n"
            f"Categories: {p.categories}\nPrice Level: {p.price_level}\n"
            f"Rating: {p.rating}\nVeg Only: {p.veg_only}\nAmbience: {p.ambience}\n"
        )
        documents.append(Document(text=txt))

    # --- Reviews ---
    for r in Review.objects.select_related('user', 'place').all():
        username = r.user.username if (r.user and getattr(r.user, 'username', None)) else 'anonymous'
        place_name = r.place.name if (r.place and getattr(r.place, 'name', None)) else 'unknown'
        txt = (
            f"REVIEW:\nUser: {username}\nPlace: {place_name}\n"
            f"Rating: {r.rating}\nComment: {r.comment or ''}\nSummary: {r.summary or ''}\n"
        )
        documents.append(Document(text=txt))

    return documents


def get_index():
    """Return a cached VectorStoreIndex built from the DB corpus.

    The index is created on first call and cached for subsequent
    queries. In production you'd persist the index to avoid rebuilds
    across process restarts.
    """
    global _CACHED_INDEX
    if _CACHED_INDEX is not None:
        return _CACHED_INDEX

    if VectorStoreIndex is None:
        raise RuntimeError("llama_index is not available; install it to enable chatbot features.")

    documents = build_corpus_from_db()
    _CACHED_INDEX = VectorStoreIndex.from_documents(documents)
    return _CACHED_INDEX


def ask_chatbot(query: str) -> str:
    """Query the chatbot index and return a text response.

    This function raises a clear RuntimeError if the required
    dependencies are not installed.
    """
    index = get_index()
    engine = index.as_query_engine()
    response = engine.query(query)
    return str(response)

