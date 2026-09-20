# Báo cáo đóng góp cá nhân — Nguyễn Văn Ước

## Thông tin

- **Họ và tên**: Nguyễn Văn Ước
- **Mã học viên**: 2A202602445
- **Nhóm**: T016
- **Repository/branch**: K4-L3A-RAG-Pipeline / main

---

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| **System Architecture & Config** | Thiết kế kiến trúc tổng thể, khắc phục tương thích môi trường Python 3.14, cấu hình biến môi trường `.env` và `pyproject.toml` | `pyproject.toml`, `.env`, `TEAMMATES.md` | Done |
| **Generation có Citation (Task 10)** | Triển khai `reorder_for_llm` giảm lost-in-the-middle, `format_context`, `call_llm` đa provider (OpenAI/Gemini/Anthropic) và `generate_with_citation` kèm Safe Refusal | `src/task10_generation.py` | Done |
| **Chatbot UI (Streamlit)** | Xây dựng giao diện Streamlit hiện đại, hiển thị badges phương thức retrieval, render expandable cards trích dẫn nguồn kèm điểm score, bộ lọc câu hỏi mẫu | `app.py` | Done |
| **Handoff & Integration** | Kiểm thử tích hợp toàn bộ pipeline từ Task 1 đến Task 10, chạy demo câu hỏi in-domain và out-of-domain | `tests/test_contracts.py`, `tests/test_acceptance.py` | Done |

---

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Thiết kế cơ chế Safe Refusal nghiêm ngặt kết hợp interleaving reordering (`reorder_for_llm`).  
   **Lý do/evidence:** Khi context thiếu bằng chứng xác thực (hoặc câu hỏi ngoài domain), mô hình bắt buộc phải trả lời từ chối an toàn thay vì bịa đặt (hallucination). Sắp xếp interleaving (đưa chunks điểm cao về đầu và cuối) giúp LLM không bị trôi thông tin quan trọng ở giữa văn bản dài.  
   **Trade-off:** Cần xử lý cẩn thận để không làm biến đổi (mutate) mảng chunk đầu vào, đảm bảo tính bất biến của dữ liệu theo đúng contract test.

2. **Quyết định:** Thiết kế UI Streamlit lưu trữ đầy đủ metadata của từng SearchResult trong `st.session_state`.  
   **Lý do/evidence:** Cho phép người dùng xem lại chính xác nguồn trích dẫn, phương thức truy xuất (Hybrid/PageIndex) và điểm score của các lượt chat trước đó mà không cần gọi lại pipeline.  
   **Trade-off:** Tăng nhẹ bộ nhớ lưu trữ session state của trình duyệt, nhưng nâng cao vượt bậc trải nghiệm người dùng và tính minh bạch của thông tin.

---

## Kiểm thử và kết quả

- **Test hoặc query tôi đã dùng:**  
  - Chạy toàn bộ test suite: `pytest -v` (20/20 test cases pass 100%).
  - Query in-domain: *"Điều kiện để nhận học bổng khuyến khích học tập loại Xuất sắc là gì?"* -> Hệ thống trả lời chính xác 100% học phí + trợ cấp 1.500.000 VNĐ/tháng kèm trích dẫn nguồn `chinh_sach_hoc_bong_tro_cap.md`.
  - Query out-of-domain: *"Thời tiết hôm nay ở Tokyo như thế nào?"* -> Hệ thống trả về Safe Refusal: *"Tôi không thể xác minh thông tin này từ nguồn hiện có."* với `sources=[]`, `retrieval_source="none"`.
- **Kết quả trước/sau:** Ban đầu `app.py` chỉ chứa placeholder `TODO`; sau khi hoàn thiện, hệ thống hoạt động end-to-end trơn tru với đầy đủ citation badges.

---

## Điều còn hạn chế

- **Hạn chế cụ thể:** Giao diện Streamlit hiện tại chưa hỗ trợ streaming token (từng từ một) khi sinh câu trả lời do dùng hàm đồng bộ `call_llm`.
- **Thay đổi đầu tiên nếu có thêm thời gian:** Tích hợp cơ chế streaming `st.write_stream` và tính năng highlight trực tiếp đoạn văn bản trích dẫn khi người dùng di chuột vào thẻ nguồn.

---

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- **Ngày:** 20/09/2026
- **Tên thành viên:** Nguyễn Văn Ước
