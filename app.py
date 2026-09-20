"""
Ứng dụng Chatbot RAG — Nhóm T016
Chủ đề: Dịch vụ & Quy chế Sinh viên Đại học

Thành viên nhóm T016:
- Nguyễn Văn Ước (2A202602445 - Trưởng nhóm — Architecture, UI & Integration)
- Trần Trọng Chinh (2A202602720 - Data Engineering & Fallback)
- Chu Minh Quân (2A202602709 - Retrieval, Reranking & Evaluation)
"""

import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation


load_dotenv()

st.set_page_config(
    page_title="Hỏi đáp Quy chế & Dịch vụ Sinh viên — Nhóm T016",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS cho giao diện thẩm mỹ, hiện đại
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(120deg, #1E3A8A 0%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .badge-hybrid {
        background-color: #E0F2FE;
        color: #0369A1;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.82rem;
        display: inline-block;
    }
    .badge-pageindex {
        background-color: #FEF3C7;
        color: #B45309;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.82rem;
        display: inline-block;
    }
    .badge-none {
        background-color: #FEE2E2;
        color: #B91C1C;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.82rem;
        display: inline-block;
    }
    .source-card {
        border-left: 3px solid #3B82F6;
        background-color: #F8FAFC;
        padding: 10px 14px;
        margin-top: 8px;
        border-radius: 0 8px 8px 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Khởi tạo session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/university.png", width=120)
    st.title("🎓 RAG Assistant — T016")
    st.markdown("**Chủ đề:** Dịch vụ & Quy chế Sinh viên")
    st.markdown("---")
    
    st.subheader("⚙️ Cấu hình truy xuất")
    top_k = st.slider("Số lượng Chunks (top_k)", min_value=3, max_value=10, value=5, step=1)
    
    st.markdown("---")
    st.subheader("👥 Thành viên Nhóm T016")
    st.markdown("""
    - **Nguyễn Văn Ước** (`2A202602445`) *(Lead - UI/Gen)*
    - **Trần Trọng Chinh** (`2A202602720`) *(Data/Fallback)*
    - **Chu Minh Quân** (`2A202602709`) *(Retrieval/Eval)*
    """)
    
    st.markdown("---")
    if st.button("🗑️ Xóa lịch sử trò chuyện"):
        st.session_state.messages = []
        st.rerun()

# Header chính
st.markdown('<div class="main-header">🎓 Trợ lý Thông tin & Quy chế Sinh viên</div>', unsafe_allow_html=True)
st.caption("Hệ thống RAG Pipeline Hybrid (Dense + BM25 + RRF) hỗ trợ tra cứu học bổng, học phí, đăng ký tín chỉ và ký túc xá.")

# Gợi ý câu hỏi nhanh theo 5 trường đại học
with st.expander("💡 Câu hỏi mẫu thử nghiệm nhanh (Click để chọn)", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏫 VinUni: Chính sách học bổng & hỗ trợ Vingroup?"):
            st.session_state.suggested_query = "Mức hỗ trợ học phí của Tập đoàn Vingroup dành cho sinh viên nhập học tại Trường Đại học VinUniversity là bao nhiêu?"
        if st.button("🏫 Bách Khoa: Học bổng Loại A (Xuất sắc)?"):
            st.session_state.suggested_query = "Học bổng Khuyến khích học tập Loại A của Đại học Bách khoa Hà Nội yêu cầu GPA và điểm rèn luyện tối thiểu bao nhiêu?"
        if st.button("🏫 ĐHQGHN: Quyết định quy định học bổng mới nhất?"):
            st.session_state.suggested_query = "Văn bản quy định hiện hành về quản lý và xét cấp học bổng sinh viên tại ĐHQGHN là văn bản nào?"
    with col2:
        if st.button("🏫 Ngoại Thương: Hệ thống FTU GATE & học phí?"):
            st.session_state.suggested_query = "Hệ thống đăng ký học phần và quản lý đào tạo tín chỉ trực tuyến của Đại học Ngoại thương tên là gì?"
        if st.button("🏫 ĐH FPT: Học bổng Giáo sư Nguyễn Văn Đạo?"):
            st.session_state.suggested_query = "Quỹ học bổng danh giá thường niên tại Đại học FPT Hà Nội mang tên vị giáo sư nào?"
        if st.button("⚠️ Câu hỏi ngoài phạm vi (Safe Refusal test)"):
            st.session_state.suggested_query = "Thời tiết hôm nay tại thủ đô Tokyo Nhật Bản như thế nào?"

# Hiển thị lịch sử tin nhắn
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Nếu là câu trả lời của trợ lý và có thông tin nguồn
        if msg.get("role") == "assistant" and msg.get("sources") is not None:
            retrieval_src = msg.get("retrieval_source", "none")
            badge_class = f"badge-{retrieval_src}"
            badge_label = f"Nguồn truy xuất: {retrieval_src.upper()}"
            st.markdown(f'<span class="{badge_class}">{badge_label}</span>', unsafe_allow_html=True)
            
            sources = msg.get("sources", [])
            if sources:
                with st.expander(f"📚 Xem {len(sources)} nguồn trích dẫn bằng chứng ({retrieval_src})"):
                    for idx, src in enumerate(sources, 1):
                        meta = src.get("metadata", {})
                        title = meta.get("title", "Tài liệu")
                        src_name = meta.get("source", "Nguồn")
                        score = src.get("score", 0.0)
                        method = src.get("retrieval_method", "hybrid")
                        
                        st.markdown(f"""
                        <div class="source-card">
                            <b>[{idx}] {title}</b> — <i>{src_name}</i><br>
                            <small>Phương thức: <b>{method}</b> | Điểm Score: <b>{score:.4f}</b></small>
                            <p style="margin-top: 6px; color: #334155;">{src.get('content', '')}</p>
                        </div>
                        """, unsafe_allow_html=True)

# Xử lý input từ chat input hoặc gợi ý
prompt_input = st.chat_input("Nhập câu hỏi về quy chế, học bổng, học phí, ký túc xá...")
query = prompt_input or st.session_state.pop("suggested_query", None)

if query:
    # Lưu và hiển thị câu hỏi của user
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Sinh câu trả lời từ RAG Pipeline
    with st.chat_message("assistant"):
        with st.spinner("Đang truy xuất ngữ cảnh và tạo câu trả lời..."):
            result = generate_with_citation(query, top_k=top_k)
            answer = result["answer"]
            sources = result["sources"]
            retrieval_source = result["retrieval_source"]

            st.markdown(answer)

            # Hiển thị badge phương thức
            badge_class = f"badge-{retrieval_source}"
            badge_label = f"Nguồn truy xuất: {retrieval_source.upper()}"
            st.markdown(f'<span class="{badge_class}">{badge_label}</span>', unsafe_allow_html=True)

            # Hiển thị chi tiết trích dẫn
            if sources:
                with st.expander(f"📚 Xem {len(sources)} nguồn trích dẫn bằng chứng ({retrieval_source})"):
                    for idx, src in enumerate(sources, 1):
                        meta = src.get("metadata", {})
                        title = meta.get("title", "Tài liệu")
                        src_name = meta.get("source", "Nguồn")
                        score = src.get("score", 0.0)
                        method = src.get("retrieval_method", "hybrid")

                        st.markdown(f"""
                        <div class="source-card">
                            <b>[{idx}] {title}</b> — <i>{src_name}</i><br>
                            <small>Phương thức: <b>{method}</b> | Điểm Score: <b>{score:.4f}</b></small>
                            <p style="margin-top: 6px; color: #334155;">{src.get('content', '')}</p>
                        </div>
                        """, unsafe_allow_html=True)

    # Lưu vào session_state
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "retrieval_source": retrieval_source,
    })
