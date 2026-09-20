"""
Task 4 — Chunking, embedding và indexing.

1. Đọc toàn bộ Markdown trong data/standardized/.
2. Chia văn bản bằng RecursiveCharacterTextSplitter.
3. Embed chunks bằng sentence_transformers (mặc định all-MiniLM-L6-v2).
4. Upsert vào ChromaDB với cosine distance.
"""

import os
import re
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DIM = 384
COLLECTION_NAME = "rag_documents"

_MODEL = None


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Tạo embedding vector cho danh sách text sử dụng SentenceTransformer."""
    if not texts:
        return []

    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer
        _MODEL = SentenceTransformer(EMBEDDING_MODEL)

    embeddings = _MODEL.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()


def get_collection():
    """Mở hoặc tạo mới Chroma collection dùng khoảng cách cosine."""
    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def load_documents() -> list[dict]:
    """Đọc Markdown trong standardized/ và trả về danh sách Document theo contract."""
    documents: list[dict] = []
    if not STANDARDIZED_DIR.exists():
        return documents

    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        if path.name.startswith("."):
            continue
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue

        doc_type = "legal" if "legal" in path.parts else "news"

        # Trích xuất title từ dòng đầu tiên nếu có định dạng Markdown heading
        title = path.stem
        lines = content.splitlines()
        for line in lines:
            line_str = line.strip()
            if line_str.startswith("# "):
                title = line_str.lstrip("# ").strip()
                break

        # Trích xuất URL từ **Source:** nếu có
        url = None
        match = re.search(r"\*\*Source:\*\*\s*(https?://[^\s]+)", content)
        if match:
            url = match.group(1).strip()
        elif doc_type == "legal":
            url = f"https://daihoc.edu.vn/van-ban-quy-che/{path.stem}"

        doc_id = path.relative_to(STANDARDIZED_DIR).as_posix()
        documents.append({
            "id": doc_id,
            "content": content,
            "metadata": {
                "source": path.name,
                "title": title,
                "doc_type": doc_type,
                "url": url,
            },
        })

    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia Document thành chunks có id duy nhất và chunk_index."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks: list[dict] = []
    for document in documents:
        splits = splitter.split_text(document["content"])
        if not splits:
            splits = [document["content"]]

        for index, text in enumerate(splits):
            chunk_content = text.strip()
            if not chunk_content:
                continue
            chunks.append({
                "id": f"{document['id']}::chunk-{index}",
                "content": chunk_content,
                "metadata": {
                    **document["metadata"],
                    "chunk_index": index,
                },
            })

    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Thêm trường embedding vào từng chunk."""
    if not chunks:
        return []
    texts = [chunk["content"] for chunk in chunks]
    vectors = embed_texts(texts)
    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector
    return chunks


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks vào ChromaDB."""
    if not chunks:
        return
    collection = get_collection()
    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=[chunk["content"] for chunk in chunks],
        embeddings=[chunk["embedding"] for chunk in chunks],
        metadatas=[chunk["metadata"] for chunk in chunks],
    )


def run_pipeline() -> None:
    """Chạy toàn bộ quá trình load, chunk, embed và index."""
    documents = load_documents()
    print(f"Loaded {len(documents)} documents.")
    chunks = chunk_documents(documents)
    print(f"Created {len(chunks)} chunks.")
    embedded_chunks = embed_chunks(chunks)
    index_to_vectorstore(embedded_chunks)
    print(f"Indexed {len(embedded_chunks)} chunks to ChromaDB at '{CHROMA_DIR}'.")


if __name__ == "__main__":
    run_pipeline()
