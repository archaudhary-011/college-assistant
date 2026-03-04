import os
import re
import pickle

import faiss
import numpy as np

from app.core.config import (
    DATA_FOLDER, INDEX_PATH, CHUNKS_PATH,
    CHUNK_SIZE, CHUNK_OVERLAP, TOP_K,
)
from app.services.embedding import get_embedding, get_model


# ── Chunking ──────────────────────────────────────────────────────────────────
def chunk_text(text: str, filename: str) -> list[dict]:
    chunks = []
    text   = text.strip()
    start  = 0

    while start < len(text):
        end   = start + CHUNK_SIZE
        chunk = text[start:end].strip()
        if chunk:
            chunks.append({"text": chunk, "source": filename, "start": start})
        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


# ── PDF Text Extraction ───────────────────────────────────────────────────────
def extract_pdf_text(path: str) -> str:
    try:
        import fitz
        doc        = fitz.open(path)
        pages_text = [page.get_text("text") for page in doc if page.get_text("text").strip()]
        doc.close()
        full_text = "\n".join(pages_text)
        full_text = re.sub(r'\n{3,}', '\n\n', full_text)
        full_text = re.sub(r'[ \t]+', ' ', full_text)
        return full_text.strip()
    except ImportError:
        print("[RAG] ❌ pymupdf not installed. Run: pip install pymupdf")
        return ""
    except Exception as e:
        print(f"[RAG] ❌ Error reading PDF: {e}")
        return ""


# ── Document Loader ───────────────────────────────────────────────────────────
def load_documents() -> list[dict]:
    all_chunks = []

    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        print(f"[RAG] Created data folder at {DATA_FOLDER}")
        return all_chunks

    all_files = os.listdir(DATA_FOLDER)
    txt_files = sorted(f for f in all_files if f.endswith(".txt"))
    pdf_files = sorted(f for f in all_files if f.endswith(".pdf"))

    print(f"[RAG] Found {len(txt_files)} TXT + {len(pdf_files)} PDF files")

    for filename in txt_files:
        try:
            with open(os.path.join(DATA_FOLDER, filename), "r", encoding="utf-8") as f:
                text = f.read()
            chunks = chunk_text(text, filename)
            all_chunks.extend(chunks)
            print(f"[RAG] ✓ TXT '{filename}' → {len(chunks)} chunks")
        except Exception as e:
            print(f"[RAG] ❌ Error loading {filename}: {e}")

    for filename in pdf_files:
        text = extract_pdf_text(os.path.join(DATA_FOLDER, filename))
        if text:
            chunks = chunk_text(text, filename)
            all_chunks.extend(chunks)
            print(f"[RAG] ✓ PDF '{filename}' → {len(chunks)} chunks")
        else:
            print(f"[RAG] ⚠ PDF '{filename}' → no text extracted")

    print(f"[RAG] ✅ Total chunks loaded: {len(all_chunks)}")
    return all_chunks


# ── FAISS Index ───────────────────────────────────────────────────────────────
def build_index(chunks: list[dict]) -> faiss.Index | None:
    if not chunks:
        return None

    print("[RAG] Building embeddings...")
    embeddings = get_embedding([c["text"] for c in chunks])
    embeddings = np.array(embeddings).astype("float32")
    faiss.normalize_L2(embeddings)

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, INDEX_PATH)
    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(chunks, f)

    print(f"[RAG] ✅ Index saved → {INDEX_PATH}")
    return index


def load_or_build_index() -> tuple:
    data_files = []
    if os.path.exists(DATA_FOLDER):
        data_files = [
            f for f in os.listdir(DATA_FOLDER)
            if f.endswith(".txt") or f.endswith(".pdf")
        ]

    if os.path.exists(INDEX_PATH) and os.path.exists(CHUNKS_PATH):
        index_mtime = os.path.getmtime(INDEX_PATH)
        data_mtimes = [os.path.getmtime(os.path.join(DATA_FOLDER, f)) for f in data_files]
        if data_mtimes and index_mtime > max(data_mtimes):
            print("[RAG] Loading cached FAISS index...")
            index = faiss.read_index(INDEX_PATH)
            with open(CHUNKS_PATH, "rb") as f:
                chunks = pickle.load(f)
            print(f"[RAG] ✅ Loaded {len(chunks)} chunks from cache.")
            return index, chunks
        print("[RAG] Data files changed — rebuilding index...")
    else:
        print("[RAG] No cached index — building fresh...")

    chunks = load_documents()
    if not chunks:
        print("[RAG] ❌ No chunks to index.")
        return None, []

    return build_index(chunks), chunks


def rebuild_index():
    global index, chunks
    for path in [INDEX_PATH, CHUNKS_PATH]:
        if os.path.exists(path):
            os.remove(path)
    index, chunks = load_or_build_index()
    print("[RAG] ✅ Index rebuilt successfully.")


# ── Search ────────────────────────────────────────────────────────────────────
def _embed_query(query: str) -> np.ndarray:
    q = np.array(get_embedding([query])).astype("float32")
    faiss.normalize_L2(q)
    return q


def search(query: str, k: int = TOP_K) -> str:
    if index is None or not chunks:
        return "No documents loaded in the knowledge base."

    scores, indices = index.search(_embed_query(query), k)
    results = [
        chunks[idx]["text"]
        for score, idx in zip(scores[0], indices[0])
        if idx >= 0 and float(score) >= 0.15
    ]
    return "\n\n---\n\n".join(results) if results else "No relevant information found."


def multi_search(queries: list[str], k: int = TOP_K) -> str:
    if index is None or not chunks:
        return "No documents loaded in the knowledge base."

    best: dict[int, float] = {}
    for query in queries:
        scores, indices = index.search(_embed_query(query), k)
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:
                best[idx] = max(best.get(idx, 0), float(score))

    top = sorted(best.items(), key=lambda x: x[1], reverse=True)[:k]
    results = [chunks[idx]["text"] for idx, score in top if score >= 0.15]
    return "\n\n---\n\n".join(results) if results else "No relevant information found."


# ── Init ──────────────────────────────────────────────────────────────────────
index, chunks = load_or_build_index()
