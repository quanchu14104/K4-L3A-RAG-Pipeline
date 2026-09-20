"""
Task 8 — PageIndex vectorless fallback.

Hướng dẫn:
    1. Đọc PAGEINDEX_API_KEY từ .env.
    2. Upload tài liệu và lưu cache document IDs.
    3. Tìm kiếm theo cấu trúc cây tài liệu và trả SearchResult có retrieval_method="pageindex".
    4. Xử lý timeout và ngoại lệ an toàn để pipeline không bị crash khi dịch vụ ngoài gián đoạn.
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CACHE_FILE = Path(__file__).parent.parent / "data" / "pageindex_cache.json"


def upload_documents() -> None:
    """Upload tài liệu lên PageIndex và lưu cache document ID."""
    if not PAGEINDEX_API_KEY:
        print("PAGEINDEX_API_KEY chưa cấu hình. Bỏ qua bước upload.")
        return

    try:
        from pageindex import PageIndexClient
        client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
        cache_data = {}

        for path in STANDARDIZED_DIR.rglob("*.md"):
            if path.name.startswith("."):
                continue
            doc_id = path.relative_to(STANDARDIZED_DIR).as_posix()
            content = path.read_text(encoding="utf-8")
            response = client.upload_document(title=path.stem, content=content)
            cache_data[doc_id] = getattr(response, "document_id", str(response))

        CACHE_FILE.write_text(json.dumps(cache_data, indent=2), encoding="utf-8")
        print(f"Uploaded {len(cache_data)} documents to PageIndex.")
    except Exception as error:
        print(f"Lỗi khi upload PageIndex: {error}")


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Tìm kiếm vectorless fallback qua PageIndex hoặc local structured parser."""
    if not PAGEINDEX_API_KEY:
        return []

    try:
        from pageindex import PageIndexClient
        client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
        response = client.search(query=query, top_k=top_k)
        results: list[dict] = []

        for idx, item in enumerate(response.get("results", [])):
            results.append({
                "id": item.get("id", f"pageindex-doc-{idx}"),
                "content": item.get("content", ""),
                "score": float(item.get("score", 1.0 - idx * 0.1)),
                "metadata": {
                    "source": item.get("source", "pageindex"),
                    "title": item.get("title", "PageIndex Document"),
                    "doc_type": "legal",
                    "url": None,
                    "chunk_index": idx,
                },
                "retrieval_method": "pageindex",
            })
        return results[:top_k]
    except Exception as error:
        # Bắt ngoại lệ để pipeline có thể xử lý fallback an toàn
        raise RuntimeError(f"PageIndex service unavailable: {error}") from error


if __name__ == "__main__":
    upload_documents()
