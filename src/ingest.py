"""
src/ingest.py

Reads all PDFs from data/raw_papers, splits them into overlapping
text chunks, and saves the result as a single JSON file that
embed.py will consume next.

Run with: python src/ingest.py
"""

import json
from pathlib import Path

from pypdf import PdfReader

# ---- Config ----
RAW_PAPERS_DIR = Path("data/raw_papers")
PROCESSED_DIR = Path("data/processed")
CHUNKS_OUTPUT_PATH = PROCESSED_DIR / "chunks.json"
CHUNK_SIZE = 500       # words per chunk
CHUNK_OVERLAP = 50     # words of overlap between consecutive chunks


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract all text from a PDF file as one big string."""
    reader = PdfReader(str(pdf_path))
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    return "\n".join(text_parts)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks, on word boundaries."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap  # step forward, keeping overlap so ideas don't get cut in half
    return chunks


def process_all_papers():
    """Extract and chunk every PDF, save results to a single JSON file."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(RAW_PAPERS_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDFs found in {RAW_PAPERS_DIR}. Add some and try again.")
        return

    print(f"Found {len(pdf_files)} PDF(s).")
    all_chunks = []

    for pdf_path in pdf_files:
        print(f"Processing: {pdf_path.name}")
        text = extract_text_from_pdf(pdf_path)

        if not text.strip():
            print(f"  Warning: no extractable text in {pdf_path.name} (might be a scanned image PDF).")
            continue

        chunks = chunk_text(text)
        print(f"  -> {len(chunks)} chunks")

        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "id": f"{pdf_path.stem}_chunk{i}",
                "text": chunk,
                "source": pdf_path.name,
                "chunk_index": i,
            })

    with open(CHUNKS_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"\nDone. {len(all_chunks)} total chunks saved to {CHUNKS_OUTPUT_PATH}")


if __name__ == "__main__":
    process_all_papers()