"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Chủ đề: Dịch vụ & Quy chế Sinh viên Đại học (Học chế tín chỉ, Học bổng, Ký túc xá).
Tạo và lưu trữ tối thiểu 3 tài liệu chính thức vào data/landing/legal/.
"""

import os
from pathlib import Path
from fpdf import FPDF


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def _create_pdf(filename: str, title: str, sections: list[tuple[str, list[str]]]) -> Path:
    """Tạo file PDF chính sách quy chuẩn đầy đủ nội dung bằng fpdf2."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    font_path = "C:/Windows/Fonts/arial.ttf"
    if os.path.exists(font_path):
        pdf.add_font("ArialVN", "", font_path)
        font_name = "ArialVN"
    else:
        font_name = "Helvetica"

    # Header
    pdf.set_font(font_name, size=16)
    pdf.cell(0, 10, text=title, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    for sec_title, paragraphs in sections:
        pdf.set_font(font_name, size=13)
        pdf.cell(0, 8, text=sec_title, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        pdf.set_font(font_name, size=10)
        for para in paragraphs:
            pdf.multi_cell(0, 6, text=para)
            pdf.ln(2)
        pdf.ln(3)

    target_path = DATA_DIR / filename
    pdf.output(str(target_path))
    return target_path


def download_documents() -> None:
    """Tạo và lưu 3 văn bản quy chế chính sách chính thức vào data/landing/legal/."""
    setup_directory()

    doc1_sections = [
        ("Chương I: Quy định chung về đào tạo tín chỉ", [
            "Điều 1. Khung thời gian và khối lượng học tập: Chương trình đào tạo cử nhân tiêu chuẩn kéo dài 4 năm tương đương 8 học kỳ chính. Tổng số tín chỉ tích lũy tối thiểu để tốt nghiệp là 135 tín chỉ đối với khối ngành kinh tế - xã hội và 150 tín chỉ đối với khối kỹ thuật - công nghệ.",
            "Điều 2. Đăng ký học phần: Mỗi học kỳ chính, sinh viên phải đăng ký tối thiểu 14 tín chỉ và tối đa không quá 24 tín chỉ (trừ học kỳ cuối khi làm đồ án/khóa luận). Trong học kỳ hè, sinh viên được đăng ký tối đa 8 tín chỉ để học cải thiện hoặc học vượt.",
            "Điều 3. Hủy và rút học phần: Sinh viên có quyền hủy học phần đã đăng ký trong 2 tuần đầu học kỳ mà không bị ghi điểm F. Rút học phần từ tuần thứ 3 đến tuần thứ 6 sẽ nhận điểm W và không được hoàn lại học phí.",
        ]),
        ("Chương II: Đánh giá kết quả học tập và thang điểm", [
            "Điều 4. Thang điểm đánh giá: Điểm học phần gồm điểm quá trình (trọng số 40% đến 50%) và điểm thi kết thúc học phần (50% đến 60%). Điểm chữ được quy đổi sang thang điểm 4: A tương ứng 4.0, B tương ứng 3.0, C tương ứng 2.0, D tương ứng 1.0 và F là 0.0.",
            "Điều 5. Xếp loại học lực tích lũy: Điểm trung bình tích lũy (CPA) từ 3.60 đến 4.00 xếp loại Xuất sắc; từ 3.20 đến 3.59 xếp loại Giỏi; từ 2.50 đến 3.19 xếp loại Khá; từ 2.00 đến 2.49 xếp loại Trung bình; dưới 2.00 xếp loại Yếu.",
            "Điều 6. Cảnh báo học vụ và buộc thôi học: Sinh viên bị cảnh báo học vụ mức 1 nếu điểm GPA học kỳ dưới 1.20 (năm nhất) hoặc dưới 1.40 (năm hai trở đi). Bị cảnh báo học vụ 2 lần liên tiếp sẽ phải chuyển xuống diện thử thách; nếu bị 3 lần cảnh báo liên tiếp sẽ bị buộc thôi học theo quy định Bộ Giáo dục và Đào tạo.",
        ]),
        ("Chương III: Điều kiện công nhận tốt nghiệp", [
            "Điều 7. Tiêu chuẩn tốt nghiệp: Tích lũy đủ số tín chỉ quy định, CPA đạt từ 2.00 trở lên, hoàn thành chứng chỉ Giáo dục thể chất và Quốc phòng - An ninh, đạt chuẩn đầu ra ngoại ngữ tương đương IELTS 6.0 hoặc TOEIC 650, và không trong thời gian bị kỷ luật từ mức đình chỉ học tập trở lên.",
        ]),
    ]

    doc2_sections = [
        ("Chương I: Các loại học bổng và tiêu chuẩn xét duyệt", [
            "Điều 1. Học bổng Khuyến khích học tập (KKHT): Được xét cấp theo từng học kỳ dựa trên kết quả học tập và rèn luyện. Mức học bổng Xuất sắc trị giá 100% học phí toàn phần cộng thêm trợ cấp sinh hoạt 1.500.000 VNĐ/tháng. Mức học bổng Giỏi trị giá 75% học phí. Mức học bổng Khá trị giá 50% học phí học kỳ.",
            "Điều 2. Điều kiện xét học bổng KKHT: Sinh viên phải đăng ký tối thiểu 15 tín chỉ trong học kỳ xét thưởng, không có môn học nào bị điểm F, điểm rèn luyện đạt từ loại Tốt (80 điểm) trở lên. Điểm GPA tối thiểu để xét học bổng Khá là 3.00, Giỏi là 3.20 và Xuất sắc là 3.60.",
            "Điều 3. Học bổng Tài trợ Doanh nghiệp và Đối tác: Dành cho sinh viên ngành Công nghệ thông tin, Trí tuệ nhân tạo và Tự động hóa có thành tích nghiên cứu khoa học xuất sắc hoặc hoàn cảnh khó khăn vươn lên trong học tập, giá trị từ 20.000.000 đến 50.000.000 VNĐ/suất.",
        ]),
        ("Chương II: Chính sách miễn giảm học phí và trợ cấp xã hội", [
            "Điều 4. Miễn 100% học phí: Áp dụng cho sinh viên là con thương binh, liệt sĩ, sinh viên khuyết tật nặng có hoàn cảnh khó khăn, hoặc sinh viên mồ côi cả cha lẫn mẹ không nơi nương tựa theo Nghị định 81/2021/NĐ-CP của Chính phủ.",
            "Điều 5. Giảm 50% học phí: Áp dụng cho sinh viên là người dân tộc thiểu số ở vùng có điều kiện kinh tế - xã hội đặc biệt khó khăn, hoặc sinh viên thuộc hộ cận nghèo theo quy định nhà nước.",
            "Điều 6. Thủ tục và thời hạn nộp hồ sơ: Hồ sơ miễn giảm học phí và xin xét học bổng nộp trực tuyến qua Cổng thông tin sinh viên từ ngày 01 đến ngày 20 của tháng đầu tiên mỗi học kỳ. Quyết định phê duyệt được công bố vào tuần thứ 5 của học kỳ.",
        ]),
    ]

    doc3_sections = [
        ("Chương I: Đối tượng ưu tiên và loại phòng lưu trú", [
            "Điều 1. Đối tượng ưu tiên bố trí chỗ ở: Ưu tiên 1 cho sinh viên diện chính sách, con thương binh liệt sĩ, người khuyết tật; Ưu tiên 2 cho sinh viên năm thứ nhất trúng tuyển nhập học; Ưu tiên 3 cho sinh viên có hộ khẩu thường trú tại vùng sâu, vùng xa có khoảng cách địa lý trên 100km.",
            "Điều 2. Phân loại phòng và đơn giá thuê: Phòng tiêu chuẩn 4 người có trang bị máy lạnh, bình nước nóng, bàn học cá nhân có giá thuê 650.000 VNĐ/sinh viên/tháng. Phòng 6 người có giá thuê 450.000 VNĐ/sinh viên/tháng. Đơn giá trên chưa bao gồm chi phí điện, nước sinh hoạt thanh toán theo chỉ số công tơ thực tế.",
        ]),
        ("Chương II: Quy định trật tự, an ninh và phòng chống cháy nổ", [
            "Điều 3. Thời gian biểu và quản lý ra vào: Ký túc xá mở cửa từ 05:30 và đóng cửa lúc 23:00 hàng ngày. Sinh viên về muộn sau 23:00 phải xuất trình thẻ sinh viên, ký sổ ghi nhận lý do tại phòng bảo vệ trực ban. Trường hợp tiếp khách ngoài phải đăng ký tại bàn lễ tân và kết thúc trước 21:30.",
            "Điều 4. An toàn điện và phòng chống cháy nổ: Nghiêm cấm sử dụng bếp gas, bếp từ cá nhân hoặc đun nấu bằng thiết bị điện công suất lớn trong phòng ngủ sinh viên. Cấm tàng trữ chất dễ cháy, nổ, vũ khí, hung khí hoặc hóa chất độc hại trong khuôn viên ký túc xá.",
            "Điều 5. Xử lý vi phạm nội quy: Sinh viên vi phạm quy định giờ giấc quá 3 lần bị khiển trách; vi phạm nấu ăn hoặc sử dụng thiết bị cấm bị tạm đình chỉ lưu trú 01 học kỳ; hành vi đánh bạc, sử dụng chất kích thích hoặc gây rối trật tự bị chấm dứt hợp đồng lưu trú vĩnh viễn và xử lý kỷ luật theo khung quy chế nhà trường.",
        ]),
    ]

    p1 = _create_pdf("quy_che_dao_tao_dai_hoc.pdf", "QUY CHẾ ĐÀO TẠO ĐẠI HỌC VÀ ĐÁNH GIÁ HỌC PHẦN", doc1_sections)
    p2 = _create_pdf("chinh_sach_hoc_bong_tro_cap.pdf", "QUY ĐỊNH CHÍNH SÁCH HỌC BỔNG VÀ HỖ TRỢ TÀI CHÍNH", doc2_sections)
    p3 = _create_pdf("noi_quy_ky_tuc_xa_sinh_vien.pdf", "NỘI QUY QUẢN LÝ VÀ LƯU TRÚ KÝ TÚC XÁ SINH VIÊN", doc3_sections)

    print(f"Generated legal doc: {p1} ({p1.stat().st_size} bytes)")
    print(f"Generated legal doc: {p2} ({p2.stat().st_size} bytes)")
    print(f"Generated legal doc: {p3} ({p3.stat().st_size} bytes)")


if __name__ == "__main__":
    download_documents()
