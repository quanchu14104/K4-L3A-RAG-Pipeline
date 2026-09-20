# Báo cáo đóng góp cá nhân — Chu Minh Quân

## Thông tin

- **Họ và tên**: Chu Minh Quân
- **Mã học viên**: 2A202602709
- **Nhóm**: T016
- **Repository/branch**: K4-L3A-RAG-Pipeline / main

---

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| **Chunking & ChromaDB Indexing (Task 4)** | Triển khai `chunk_documents` (RecursiveSplitter), `embed_texts` với sentence-transformers, tạo collection ChromaDB cosine distance và index 35 chunks | `src/task4_chunking_indexing.py`, `chroma_db/` | Done |
| **Dense & BM25 Search (Tasks 5 & 6)** | Hoàn thiện `semantic_search` quy đổi cosine distance sang similarity; triển khai `SafeBM25Okapi` với công thức Lucene IDF tránh lỗi IDF=0 | `src/task5_semantic_search.py`, `src/task6_lexical_search.py` | Done |
| **Reciprocal Rank Fusion (Task 7 & 9)** | Triển khai thuật toán `rerank_rrf` ($RRF = \sum 1/(k+rank)$) sao chép item an toàn, tích hợp pipeline `retrieve` với threshold calibration 0.30 | `src/task7_reranking.py`, `src/task9_retrieval_pipeline.py` | Done |
| **Đánh giá A/B & Golden Dataset** | Xây dựng bộ 16 ca kiểm thử ground-truth, chạy đo 4 metrics (Faithfulness, Relevance, Recall, Precision), phân tích 3 worst performers và đề xuất cải tiến | `group_project/evaluation/golden_dataset.json`, `group_project/evaluation/RESULT.md` | Done |

---

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Cải tiến công thức tính IDF trong BM25 sang công thức chuẩn Lucene: $\ln(1 + \frac{N - n + 0.5}{n + 0.5})$.  
   **Lý do/evidence:** Trong công thức BM25 gốc, khi corpus nhỏ (hoặc trong unit test có 2 tài liệu), từ khóa xuất hiện ở 1 tài liệu sẽ cho $IDF = \ln(1) = 0$, dẫn đến điểm BM25 bằng 0 và làm rớt kết quả tìm kiếm. Công thức cải tiến đảm bảo IDF luôn dương và ổn định trong mọi quy mô dữ liệu.  
   **Trade-off:** Cần kế thừa `SafeBM25Okapi` từ `rank_bm25.BM25Okapi` và ghi đè phương thức `_calc_idf`.

2. **Quyết định:** Hiệu chỉnh ngưỡng `SCORE_THRESHOLD = 0.30` dựa trên phân tích phân bố điểm cosine similarity.  
   **Lý do/evidence:** Thử nghiệm với các câu hỏi trong domain cho điểm cosine cao nhất đạt 0.75 - 0.82; trong khi câu hỏi ngoài domain (out-of-domain) chỉ đạt 0.12 - 0.18. Ngưỡng 0.30 tạo ra ranh giới phân định rõ ràng để kích hoạt fallback an toàn.  
   **Trade-off:** Không thể áp dụng cứng một ngưỡng 0.30 cho mọi corpus khác mà cần hiệu chỉnh lại nếu thay đổi mô hình embedding.

---

## Kiểm thử và kết quả

- **Test hoặc query tôi đã dùng:**  
  - Chạy contract tests cho retrieval: `pytest tests/test_contracts.py -k "chunk or semantic or lexical or rrf or retrieve"` (10/10 test pass).
  - Chạy acceptance tests cho golden dataset và report: `pytest tests/test_acceptance.py -k "golden or evaluation"` (2/2 test pass).
  - Kết quả so sánh A/B: Config B (Hybrid + RRF) đạt điểm trung bình 0.941, vượt trội hơn Config A (Dense-only) đạt 0.844 (+0.097).
- **Kết quả trước/sau:** Các hàm search ban đầu đều là `NotImplementedError`; sau khi hoàn thiện, cả hai đường dense và lexical kết hợp RRF hoạt động hoàn hảo và vượt qua 100% test cases.

---

## Điều còn hạn chế

- **Hạn chế cụ thể:** Tham số $k$ trong RRF hiện đang cố định là 60 theo thông lệ chuẩn; chưa thực hiện grid-search để tìm giá trị tối ưu riêng cho bộ dữ liệu tiếng Việt.
- **Thay đổi đầu tiên nếu có thêm thời gian:** Thử nghiệm tích hợp thêm Cross-Encoder reranker (`bge-reranker-base`) làm lớp reranking cấp hai sau RRF.

---

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- **Ngày:** 20/09/2026
- **Tên thành viên:** Chu Minh Quân
