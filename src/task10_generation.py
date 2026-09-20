"""
Task 10 — Generation có citation.

1. Retrieve top-k chunks từ Task 9.
2. Reorder để giảm thiểu hiện tượng lost-in-the-middle.
3. Format context kèm nhãn title và source rõ ràng.
4. Gọi LLM provider theo .env (OpenAI, Gemini, Anthropic hoặc local synthesis).
5. Trả answer, sources và retrieval_source chuẩn hợp đồng GenerationResult.
"""

import os
import re
from dotenv import load_dotenv

from .task9_retrieval_pipeline import retrieve


load_dotenv()

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
LLM_MODEL = os.getenv("LLM_MODEL", "")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

SYSTEM_PROMPT = """Bạn là trợ lý AI giải đáp thông tin quy chế và dịch vụ sinh viên đại học.
Quy tắc bắt buộc:
1. Trả lời CHỈ dựa trên context được cung cấp.
2. Mỗi thông tin khẳng định phải kèm trích dẫn nguồn rõ ràng dạng [Document X | Source: ...].
3. Nếu context không có đủ bằng chứng xác thực để trả lời câu hỏi, hãy trả lời chính xác: 'Tôi không thể xác minh thông tin này từ nguồn hiện có.' và tuyệt đối không tự suy diễn hoặc bịa đặt thông tin."""

SAFE_REFUSAL_ANSWER = "Tôi không thể xác minh thông tin này từ nguồn hiện có."


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa các chunks quan trọng nhất về đầu và cuối context (giảm lost-in-the-middle)."""
    if len(chunks) <= 2:
        return list(chunks)
    front = chunks[::2]
    back = chunks[1::2]
    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title và source label chuẩn hóa."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        meta = chunk.get("metadata", {})
        title = meta.get("title", "Tài liệu")
        source = meta.get("source", "Nguồn")
        parts.append(
            f"[Document {index} | Title: {title} | Source: {source}]\n{chunk['content']}"
        )
    return "\n\n---\n\n".join(parts)


def _local_synthesize(system_prompt: str, user_message: str) -> str:
    """Tổng hợp câu trả lời dựa trên context cục bộ khi chưa cấu hình API Key ngoài."""
    query_str = ""
    if "Câu hỏi:" in user_message:
        query_str = user_message.split("Câu hỏi:")[1].split("\n")[0].strip().lower()

    if "Context được cung cấp:" in user_message:
        ctx_part = user_message.split("Context được cung cấp:")[1].split("Câu hỏi:")[0].strip()
    else:
        ctx_part = user_message

    if not ctx_part:
        return SAFE_REFUSAL_ANSWER

    # Kiểm tra tính liên quan giữa câu hỏi và context
    domain_keywords = {
        "học bổng", "học phí", "tín chỉ", "học kỳ", "sinh viên", "ký túc xá",
        "phòng", "đăng ký", "thư viện", "giáo trình", "quy chế", "cảnh báo",
        "tốt nghiệp", "điểm", "gpa", "cpa", "nội quy", "bồi hoàn", "khuyến khích"
    }
    if query_str and not any(kw in query_str for kw in domain_keywords):
        return SAFE_REFUSAL_ANSWER

    doc_blocks = re.findall(
        r"\[Document (\d+) \| Title: ([^\|]+) \| Source: ([^\]]+)\]\n(.*?)(?=\n\n---\n\n|\Z)",
        ctx_part,
        re.DOTALL,
    )
    if not doc_blocks:
        return SAFE_REFUSAL_ANSWER

    lines = [
        "Dựa trên các tài liệu và quy định chính thức được cung cấp, câu trả lời chi tiết như sau:\n"
    ]
    for doc_num, title, source, content in doc_blocks[:3]:
        summary_line = content.strip().split("\n")[0]
        lines.append(f"- **Theo {title.strip()}** ([Document {doc_num} | Source: {source.strip()}]): {summary_line}")

    lines.append("\n*Lưu ý: Mọi thông tin trên đều được trích xuất trực tiếp từ văn bản quy định của nhà trường.*")
    return "\n".join(lines)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi OpenAI, Gemini hoặc Anthropic theo cấu hình trong .env."""
    provider = LLM_PROVIDER.lower()

    if provider == "openai" and OPENAI_API_KEY:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        model = LLM_MODEL or "gpt-4o-mini"
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=TEMPERATURE,
            top_p=TOP_P,
        )
        return response.choices[0].message.content or ""

    elif provider == "gemini" and GEMINI_API_KEY:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        model = LLM_MODEL or "gemini-2.5-flash"
        response = client.models.generate_content(
            model=model,
            contents=f"{system_prompt}\n\n{user_message}",
        )
        return response.text or ""

    elif provider == "anthropic" and ANTHROPIC_API_KEY:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        model = LLM_MODEL or "claude-3-5-haiku-20241022"
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            temperature=TEMPERATURE,
        )
        return response.content[0].text or ""

    return _local_synthesize(system_prompt, user_message)


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về kết quả GenerationResult theo chuẩn hợp đồng."""
    chunks = retrieve(query, top_k=top_k)

    if not chunks:
        return {
            "answer": SAFE_REFUSAL_ANSWER,
            "sources": [],
            "retrieval_source": "none",
        }

    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)

    user_message = (
        f"Context được cung cấp:\n{context}\n\n"
        f"Câu hỏi: {query}\n\n"
        "Hãy trả lời câu hỏi chi tiết dựa trên context trên và trích dẫn rõ nguồn dạng [Document X | Source: Y]."
    )

    answer = call_llm(SYSTEM_PROMPT, user_message)
    if not answer or not answer.strip() or SAFE_REFUSAL_ANSWER in answer:
        return {
            "answer": SAFE_REFUSAL_ANSWER,
            "sources": [],
            "retrieval_source": "none",
        }

    raw_method = chunks[0].get("retrieval_method", "hybrid")
    retrieval_source = raw_method if raw_method in {"hybrid", "pageindex"} else "hybrid"

    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": retrieval_source,
    }


if __name__ == "__main__":
    result = generate_with_citation("Điều kiện nhận học bổng khuyến khích học tập?")
    print(f"Answer:\n{result['answer']}")
    print(f"Sources count: {len(result['sources'])}")
    print(f"Retrieval source: {result['retrieval_source']}")
