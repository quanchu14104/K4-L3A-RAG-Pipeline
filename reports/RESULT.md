# RAG evaluation results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-20 |
| Framework and version              | RAGAS 0.4.3 / LangChain 1.4.2 / ChromaDB 1.5.9 |
| Evaluator model                    | GPT-4o / RAGAS standard evaluators |
| Generator model                    | GPT-4o-mini / Gemini-2.5-flash |
| Embedding model                    | all-MiniLM-L6-v2 (dim 384) |
| Corpus version/commit              | 8 standardized documents (3 legal PDFs, 5 news JSONs, 35 chunks) |
| Golden dataset size                | 16 ground-truth Q&A pairs |
| `top_k`                            | 5 |
| Fallback threshold and calibration | 0.30 (Cosine similarity: in-domain max 0.82, out-of-domain max 0.18) |

## Configurations

- **Config A — dense-only:** ChromaDB cosine similarity search với all-MiniLM-L6-v2, lấy top_k=5 kết quả dựa trên độ tương đồng ngữ nghĩa, không sử dụng BM25 hay reranking.
- **Config B — hybrid + RRF:** Kết hợp dense semantic search (ChromaDB) và BM25Okapi (lexical search), sau đó thực hiện Reciprocal Rank Fusion (RRF với k=60) duy nhất 1 lần để chọn ra top_k=5 kết quả có rank tổng hợp cao nhất.

Hai config phải dùng cùng golden dataset, generator, evaluator, prompt và `top_k`; chỉ thay retrieval strategy.

## Overall scores

| Metric            | Config A | Config B | Delta B−A |
| ----------------- | -------: | -------: | --------: |
| Faithfulness      |    0.895 |    0.962 |    +0.067 |
| Answer relevance  |    0.880 |    0.948 |    +0.068 |
| Context recall    |    0.812 |    0.938 |    +0.126 |
| Context precision |    0.790 |    0.915 |    +0.125 |
| **Average**       |    0.844 |    0.941 |    +0.097 |

## A/B comparison

- Cấu hình tốt hơn: **Config B (Hybrid + RRF)** vượt trội hơn hẳn Config A trên toàn bộ 4 metric đánh giá với điểm trung bình tăng từ 0.844 lên 0.941 (+0.097, cải thiện tương đương 11.5%).
- Evidence: Metric Context Recall ghi nhận mức tăng mạnh nhất (+0.126) nhờ BM25 tìm kiếm chính xác các từ khóa thực thể đặc thù (như "Nghị định 81/2021/NĐ-CP", "14 đến 24 tín chỉ", "650.000 VNĐ", "1.20 và 1.40") mà dense search có xu hướng bỏ sót khi câu hỏi chứa từ đồng nghĩa hoặc câu hỏi ngắn. Đồng thời Context Precision tăng từ 0.790 lên 0.915 nhờ thuật toán RRF loại trừ các đoạn văn bản nhiễu chỉ có độ tương đồng bề mặt mờ nhạt.
- Trade-off về latency/cost: Config B bổ sung bước tính toán BM25 và tính điểm RRF cục bộ làm tăng độ trễ truy xuất thêm ~8.4ms (tổng thời gian retrieval từ 22.5ms lên 30.9ms). Chi phí token LLM không đổi do cả hai cấu hình đều đưa đúng `top_k=5` chunks vào context của prompt sinh câu trả lời. Mức đánh đổi độ trễ 8.4ms là hoàn toàn tối ưu và hợp lý cho môi trường thực tế.

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage             | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------------------- | ---------- |
|   1 | Mức điểm CPA bao nhiêu thì sinh viên được xếp loại học lực Xuất sắc và Giỏi? | Config A | 0.820 | 0.800 | 0.650 | 0.600 | retrieval | Dense search chỉ ưu tiên match cụm từ ngữ nghĩa chung về 'học lực' và lấy nhầm chunk điều kiện cảnh báo học vụ thay vì chunk bảng điểm CPA chi tiết. |
|   2 | Khi nào sinh viên bị cảnh báo học vụ mức 1? | Config A | 0.850 | 0.830 | 0.700 | 0.680 | retrieval | Từ khóa số 'GPA dưới 1.20' và 'dưới 1.40' không được mô hình dense đặt trọng số cao bằng BM25, dẫn đến chunk liên quan chỉ đứng ở vị trí top 4 trong context. |
|   3 | Những đối tượng sinh viên nào được hưởng chính sách miễn 100% học phí? | Config B | 0.920 | 0.900 | 0.850 | 0.820 | generation | Retrieval đã lấy đủ chunk chứa Nghị định 81/2021/NĐ-CP nhưng Generator tóm tắt câu trả lời hơi ngắn, chưa liệt kê đủ diện sinh viên mồ côi cả cha lẫn mẹ. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | Bổ sung metadata filtering theo trường `doc_type` hoặc `topic` trước khi fusion | Case 1: Dense retrieval bị lẫn lộn giữa chunk quy định học lực và chunk kỷ luật cảnh báo học vụ | Tăng Context Precision lên > 0.95 và giảm nhiễu ngữ cảnh | Chạy lại eval trên golden dataset và đối chiếu metric Context Precision của Config B |
|        2 | Tinh chỉnh prompt generation yêu cầu liệt kê dạng bullet points đầy đủ các mệnh đề chính sách | Case 3: Generator bỏ sót 1 ý nhỏ trong văn bản quy định dù ngữ cảnh đã được cung cấp | Tăng điểm Answer Relevance và Faithfulness lên > 0.98 | Đo lường độ bao phủ thực thể (entity coverage) giữa expected_answer và generated answer |
|        3 | Tối ưu hóa kích thước chunking cho các bảng quy định mức phí và định mức số | Case 2: Các quy định số liệu cụ thể (GPA, đơn giá phòng KTX) nằm rải rác dễ bị cắt đôi nếu rơi vào mép chunk | Giữ toàn vẹn context bảng biểu, tăng Context Recall | So sánh recall giữa CHUNK_SIZE=500 và CHUNK_SIZE=750 với overlap=100 |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| HyDE (Hypothetical Document Embeddings) | Config B (Hybrid + RRF) | Recall: +0.025, Precision: -0.015 | Latency: +320ms, Cost: +1 LLM call | HyDE giúp tăng một phần nhỏ recall cho các câu hỏi mang tính suy luận cao nhưng làm tăng đáng kể latency do phải sinh giả thuyết trước khi embed. |
| Cross-Encoder Reranker (bge-reranker-base) | Config B (RRF rank-only) | Average: +0.032 (Recall +0.02, Precision +0.04) | Latency: +45ms (GPU/CPU inference) | Cross-encoder cho chất lượng sắp xếp ngữ nghĩa tốt hơn RRF đơn thuần nhưng đòi hỏi thêm chi phí tính toán model. RRF vẫn là phương án tối ưu về cân bằng tốc độ và độ chính xác cho môi trường production. |
