"""
Task 5 — Semantic search.

Embed query bằng chính hàm của Task 4, query ChromaDB và đổi cosine distance
thành similarity. Output phải theo SearchResult, sort giảm dần và không quá top_k.
"""

from .task4_chunking_indexing import embed_texts, get_collection


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về dense SearchResult theo score giảm dần."""
    query_vector = embed_texts([query])[0]
    collection = get_collection()
    response = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    if not response or not response.get("ids") or not response["ids"][0]:
        return []

    results: list[dict] = []
    seen_ids = set()

    for item_id, content, meta, distance in zip(
        response["ids"][0],
        response["documents"][0],
        response["metadatas"][0],
        response["distances"][0],
    ):
        if item_id in seen_ids:
            continue
        seen_ids.add(item_id)

        # Cosine distance -> Cosine similarity
        similarity = max(0.0, 1.0 - float(distance))
        results.append({
            "id": item_id,
            "content": content,
            "score": similarity,
            "metadata": meta,
            "retrieval_method": "dense",
        })

    # Đảm bảo sắp xếp giảm dần theo score và giới hạn tối đa top_k
    sorted_results = sorted(results, key=lambda item: item["score"], reverse=True)
    return sorted_results[:top_k]


if __name__ == "__main__":
    for res in semantic_search("quy chế đào tạo tín chỉ", top_k=3):
        print(f"[{res['score']:.4f}] {res['id']}: {res['content'][:80]}...")
