"""
Task 3 — Chuẩn hóa dữ liệu sang Markdown.

1. Dùng MarkItDown để convert PDF/DOCX sang standardized/legal/*.md.
2. Đọc JSON từ landing/news và format sang standardized/news/*.md kèm header metadata.
3. Bảo đảm độ dài tối thiểu > 200 ký tự cho mỗi file.
"""

import json
from pathlib import Path
from markitdown import MarkItDown


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def convert_legal_docs() -> None:
    """Convert tài liệu pháp lý/quy chế từ PDF sang Markdown."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    converter = MarkItDown()
    for path in legal_dir.iterdir():
        if path.suffix.lower() in {".pdf", ".doc", ".docx"} and not path.name.startswith("."):
            result = converter.convert(str(path))
            out_file = output_dir / f"{path.stem}.md"
            out_file.write_text(result.text_content, encoding="utf-8")
            print(f"Converted legal: {out_file.name} ({len(result.text_content)} chars)")


def convert_news_articles() -> None:
    """Convert tin tức từ JSON sang Markdown kèm header metadata."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    for path in sorted(news_dir.glob("*.json")):
        if path.name.startswith("."):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        header = (
            f"# {data['title']}\n\n"
            f"**Source:** {data['url']}\n\n"
            f"**Crawled:** {data['date_crawled']}\n\n---\n\n"
        )
        content = header + data.get("content_markdown", "")
        out_file = output_dir / f"{path.stem}.md"
        out_file.write_text(content, encoding="utf-8")
        print(f"Converted news: {out_file.name} ({len(content)} chars)")


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing sang standardized."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Standardized Markdown saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
