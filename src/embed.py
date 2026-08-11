"""
src/embed.py

Loads the chunks produced by ingest.py, embeds them, and stores
them in a persistent local ChromaDB vector store.

Run with: python src/embed.py
(after running ingest.py first)
"""

import json
from pathlib import Path

from sentence_transformers import SentenceTransformer
import chromadb

# ---- Config ----
PROCESSED_DIR = Path("data/processed")
CHUNKS_INPUT_PATH = PROCESSED_DIR / "chunks.json"
CHROMA_DIR = Path("data/chroma_db")
COLLECTION_NAME = "swim_papers"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def load_chunks() -> list[dict]:
    """Load the chunks JSON produced by ingest.py."""
    if not CHUNKS_INPUT_PATH.exists():
        raise FileNotFoundError(
            f"{CHUNKS_INPUT_PATH} not found. Run 'python src/ingest.py' first."
        )
    with open(CHUNKS_INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def embed_and_store(chunks: list[dict]):
    """Embed all chunks and store them in a persistent Chroma collection."""
    print("Loading embedding model...")
    embedder = SentenceTransformer(EMBEDDING_MODEL)

    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

    texts = [c["text"] for c in chunks]
    ids = [c["id"] for c in chunks]
    metadatas = [{"source": c["source"], "chunk_index": c["chunk_index"]} for c in chunks]

    print(f"Embedding {len(texts)} chunks...")
    embeddings = embedder.encode(texts).tolist()  # batch-embed, faster than one at a time

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    print(f"Done. {len(texts)} chunks stored in Chroma at {CHROMA_DIR}")


if __name__ == "__main__":
    chunks = load_chunks()
    embed_and_store(chunks)