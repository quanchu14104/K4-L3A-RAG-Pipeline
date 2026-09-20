"""
Task 9 — Retrieval pipeline hoàn chỉnh.

Luồng xử lý:
    1. Chạy semantic_search và lexical_search.
    2. Kiểm tra best cosine score gốc từ dense results so với score_threshold.
    3. Nếu score dưới threshold, thử PageIndex fallback.
    4. Nếu fallback trả về kết quả, dùng kết quả đó.
    5. Nếu score đủ tự tin hoặc fallback lỗi/trống, fuse bằng RRF đúng một lần.

Tuyệt đối không so sánh threshold với RRF score vì hai thang đo khác nhau.
"""

import os
from dotenv import load_dotenv

from .task5_semantic_search import semantic_search
from .task6_lexical_search import lexical_search
from .task7_reranking import rerank_rrf
from .task8_pageindex_vectorless import pageindex_search


load_dotenv()

threshold_env = os.getenv("SCORE_THRESHOLD", "").strip()
SCORE_THRESHOLD = float(threshold_env) if threshold_env else 0.3
DEFAULT_TOP_K = 5


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> list[dict]:
    """Trả về hybrid hoặc pageindex SearchResult."""
    dense = semantic_search(query, top_k=top_k * 2)
    sparse = lexical_search(query, top_k=top_k * 2)

    best_dense_score = dense[0]["score"] if dense else 0.0

    # Nếu dense score không đủ tự tin, thử fallback sang PageIndex
    if best_dense_score < score_threshold:
        try:
            fallback = pageindex_search(query, top_k=top_k)
            if fallback:
                return fallback[:top_k]
        except Exception:
            # Nếu provider fallback gặp sự cố, tiếp tục dùng kết quả hybrid
            pass

    # Nếu dense tự tin hoặc fallback không khả dụng, thực hiện fusion
    if use_reranking:
        return rerank_rrf([dense, sparse], top_k=top_k)
    return dense[:top_k]


if __name__ == "__main__":
    for res in retrieve("quy chế đào tạo", top_k=3):
        print(f"[{res['retrieval_method']}] {res['id']}: score={res['score']}")
