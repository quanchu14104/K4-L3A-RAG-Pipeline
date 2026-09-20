"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""

import math
import numpy as np
from rank_bm25 import BM25Okapi


CORPUS: list[dict] = []


class SafeBM25Okapi(BM25Okapi):
    """BM25Okapi với công thức IDF chuẩn Lucene: log(1 + (N - n + 0.5)/(n + 0.5)).
    
    Ngăn chặn việc IDF = 0 khi corpus nhỏ (ví dụ corpus có 2 tài liệu trong unit test).
    """

    def _calc_idf(self, nd):
        for word, freq in nd.items():
            self.idf[word] = math.log(1.0 + (self.corpus_size - freq + 0.5) / (freq + 0.5))


def get_corpus() -> list[dict]:
    """Lấy corpus chunks mặc định từ Task 4 nếu chưa được khởi tạo."""
    global CORPUS
    if not CORPUS:
        from .task4_chunking_indexing import chunk_documents, load_documents
        CORPUS = chunk_documents(load_documents())
    return CORPUS


def build_bm25_index(corpus: list[dict]) -> SafeBM25Okapi:
    """Tạo BM25 index từ danh sách chunks."""
    tokenized = [item["content"].lower().split() for item in corpus]
    return SafeBM25Okapi(tokenized)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    corpus = CORPUS if CORPUS else get_corpus()
    if not corpus or not query.strip():
        return []

    tokens = query.lower().split()
    if not tokens:
        return []

    bm25 = build_bm25_index(corpus)
    scores = bm25.get_scores(tokens)
    indices = np.argsort(scores)[::-1]

    results: list[dict] = []
    seen_ids = set()

    for index in indices:
        if len(results) >= top_k:
            break
        score = float(scores[index])
        if score <= 0:
            continue
        item = corpus[index]
        if item["id"] in seen_ids:
            continue
        seen_ids.add(item["id"])

        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": score,
            "metadata": item["metadata"],
            "retrieval_method": "bm25",
        })

    return results


if __name__ == "__main__":
    for res in lexical_search("học bổng trợ cấp", top_k=3):
        print(f"[{res['score']:.4f}] {res['id']}: {res['content'][:80]}...")
