"""טעינת מסמכי TXT, Markdown ו-PDF מתיקיית בסיס הידע."""
from pathlib import Path
from pypdf import PdfReader



# הפונקציה הבאה מממשת שלב מוגדר בתהליך העבודה של האפליקציה.
def load_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")



# הפונקציה הבאה מממשת שלב מוגדר בתהליך העבודה של האפליקציה.
def load_pdf_file(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)



# הפונקציה הבאה מממשת שלב מוגדר בתהליך העבודה של האפליקציה.
def load_documents(data_dir: str = "data") -> list[dict]:
    """Load PDF/TXT/MD files from data directory."""
    base = Path(data_dir)
    docs = []
    for path in base.rglob("*"):
        if path.is_dir():
            continue
        if path.suffix.lower() not in {".txt", ".md", ".pdf"}:
            continue

        if path.suffix.lower() == ".pdf":
            text = load_pdf_file(path)
        else:
            text = load_text_file(path)

        docs.append({
            "text": text,
            "source": str(path),
            "category": path.parent.name,
        })
    return docs
