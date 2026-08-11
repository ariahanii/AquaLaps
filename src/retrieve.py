"""
src/retrieve.py

Given a text query (e.g. a user's training goal), embeds it and
retrieves the most relevant chunks from the ChromaDB collection
built by embed.py.

Run directly for a quick test: python src/retrieve.py
"""

from pathlib import Path

from sentence_transformers import SentenceTransformer
import chromadb

# ---- Config (must match embed.py) ----
CHROMA_DIR = Path("data/chroma_db")
COLLECTION_NAME = "swim_papers"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_TOP_K = 5

# Loaded once and reused across calls, since loading the model / opening
# the DB connection is the slow part — you don't want to redo it per query.
_embedder = None
_collection = None


def _get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBEDDING_MODEL)
    return _embedder


def _get_collection():
    global _collection
    if _collection is None:
        chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    return _collection


def retrieve_chunks(query: str, top_k: int = DEFAULT_TOP_K) -> list[dict]:
    """
    Given a query string, return the top_k most relevant chunks.

    Each result is a dict: {"text": ..., "source": ..., "chunk_index": ..., "distance": ...}
    distance = how far the chunk is from the query in embedding space (lower = more relevant).
    """
    embedder = _get_embedder()
    collection = _get_collection()

    query_embedding = embedder.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
    )

    chunks = []
    # Chroma returns results as parallel lists nested one level deep (one list per query)
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for doc, meta, dist in zip(documents, metadatas, distances):
        chunks.append({
            "text": doc,
            "source": meta["source"],
            "chunk_index": meta["chunk_index"],
            "distance": dist,
        })

    return chunks


def format_chunks_for_prompt(chunks: list[dict]) -> str:
    """
    Turn retrieved chunks into a single text block, ready to drop into
    an LLM prompt, with source citations so the model (and you) can trace
    each piece of context back to its paper.
    """
    formatted_parts = []
    for chunk in chunks:
        formatted_parts.append(
            f"[Source: {chunk['source']}, chunk {chunk['chunk_index']}]\n{chunk['text']}"
        )
    return "\n\n---\n\n".join(formatted_parts)


if __name__ == "__main__":
    #test_query = "training plan for improving 100m freestyle time"
    test_query = "weight loss through swimming"
    print(f"Query: {test_query}\n")

    results = retrieve_chunks(test_query, top_k=3)

    for i, chunk in enumerate(results, start=1):
        print(f"Result {i} (distance={chunk['distance']:.4f}, source={chunk['source']})")
        print(chunk["text"][:200] + "...\n")