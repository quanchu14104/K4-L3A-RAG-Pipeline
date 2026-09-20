# Báo cáo đóng góp cá nhân — Trần Trọng Chinh

## Thông tin

- **Họ và tên**: Trần Trọng Chinh
- **Mã học viên**: 2A202602720
- **Nhóm**: T016
- **Repository/branch**: K4-L3A-RAG-Pipeline / main

---

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| **Thu thập tài liệu chính sách (Task 1)** | Xây dựng script tạo và chuẩn bị 3 văn bản chính sách PDF thực tế (> 1KB mỗi file) về đào tạo tín chỉ, học bổng và nội quy ký túc xá | `src/task1_collect_legal_docs.py`, `data/landing/legal/` | Done |
| **Crawl bài viết/thông báo (Task 2)** | Triển khai thu thập 5 bài viết thông báo định dạng JSON kèm đầy đủ metadata (`url`, `title`, `date_crawled`, `content_markdown`) | `src/task2_crawl_news.py`, `data/landing/news/` | Done |
| **Chuẩn hóa Markdown (Task 3)** | Xử lý chuyển đổi toàn bộ PDF và JSON sang Markdown chuẩn hóa trong `data/standardized/`, kiểm soát độ dài > 200 ký tự | `src/task3_convert_markdown.py`, `data/standardized/` | Done |
| **Vectorless Fallback (Task 8)** | Xây dựng module kết nối PageIndex, cơ chế cache ID tài liệu và xử lý ngoại lệ an toàn tránh crash hệ thống | `src/task8_pageindex_vectorless.py` | Done |

---

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Sử dụng MarkItDown để trích xuất cấu trúc văn bản từ tài liệu PDF chính sách.  
   **Lý do/evidence:** MarkItDown bảo toàn được cấu trúc phân cấp (chương, điều, khoản) thay vì làm phẳng văn bản như các công cụ trích xuất thô thông thường, giúp các chunk sau này giữ được ngữ cảnh toàn vẹn.  
   **Trade-off:** Cần cài đặt thêm các phụ thuộc thư viện xử lý tài liệu, nhưng kết quả Markdown thu được có chất lượng vượt trội cho bước embedding.

2. **Quyết định:** Thiết kế module Fallback PageIndex có cơ chế bắt lỗi (try-catch) toàn diện.  
   **Lý do/evidence:** PageIndex là dịch vụ web bên ngoài (external cloud service), có thể gặp sự cố mạng hoặc hết hạn API key. Cơ chế fallback phải đảm bảo khi dịch vụ ngoài lỗi thì pipeline vẫn trả về kết quả hybrid cục bộ mà không bị gián đoạn.  
   **Trade-off:** Cần kiểm thử thêm trường hợp mock lỗi dịch vụ mạng để đảm bảo pipeline luôn sống.

---

## Kiểm thử và kết quả

- **Test hoặc query tôi đã dùng:**  
  - Chạy kiểm thử chấp nhận dữ liệu: `pytest tests/test_acceptance.py -k "corpus or standardized"` (3/3 test pass).
  - Kiểm tra file kích thước và định dạng: cả 3 file PDF đều > 35KB; cả 8 file Markdown đều > 1300 ký tự.
  - Kiểm thử fallback chịu lỗi: `test_retrieve_survives_fallback_provider_error` pass 100%.
- **Kết quả trước/sau:** Từ thư mục landing trống rỗng ban đầu, toàn bộ corpus đã được thu thập, chuẩn hóa đầy đủ và vượt qua toàn bộ các bài acceptance test.

---

## Điều còn hạn chế

- **Hạn chế cụ thể:** Tập dữ liệu hiện tại tập trung vào 8 văn bản cốt lõi; chưa tự động đồng bộ RSS từ website trường học theo thời gian thực.
- **Thay đổi đầu tiên nếu có thêm thời gian:** Xây dựng Cron job định kỳ tự động crawl các thông báo học vụ mới nhất từ cổng thông tin đào tạo.

---

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- **Ngày:** 20/09/2026
- **Tên thành viên:** Trần Trọng Chinh
