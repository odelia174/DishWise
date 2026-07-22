"""חלוקת טקסט לקטעים חופפים לצורך שמירה וחיפוש במערכת RAG."""

# הפונקציה הבאה מממשת שלב מוגדר בתהליך העבודה של האפליקציה.
def split_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    """Split text into overlapping chunks for RAG."""
    text = " ".join(text.split())
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = max(0, end - overlap)
    return chunks
