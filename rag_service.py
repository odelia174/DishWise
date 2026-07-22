"""שירות RAG: יצירת Embeddings, ניהול ChromaDB ושליפת מקורות רלוונטיים."""
import os
import uuid
import chromadb
from services.openai_service import get_client
from utils.document_loader import load_documents
from utils.text_splitter import split_text

COLLECTION_NAME = "dishwise_knowledge"


# הפונקציה הבאה מממשת שלב מוגדר בתהליך העבודה של האפליקציה.
def get_embedding_model() -> str:
    return os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")


# הפונקציה הבאה מממשת שלב מוגדר בתהליך העבודה של האפליקציה.
def get_chroma_client():
    path = os.getenv("CHROMA_PATH", "./chroma_db")
    return chromadb.PersistentClient(path=path)


# הפונקציה הבאה מממשת שלב מוגדר בתהליך העבודה של האפליקציה.
def embed_texts(texts: list[str]) -> list[list[float]]:
    client = get_client()
    result = client.embeddings.create(
        model=get_embedding_model(),
        input=texts,
    )
    return [item.embedding for item in result.data]


# הפונקציה הבאה מממשת שלב מוגדר בתהליך העבודה של האפליקציה.
def build_knowledge_base(data_dir: str = "data") -> int:
    chroma = get_chroma_client()
    collection = chroma.get_or_create_collection(name=COLLECTION_NAME)

    docs = load_documents(data_dir)
    ids, chunks, metadatas = [], [], []

    for doc in docs:
        for chunk in split_text(doc["text"]):
            ids.append(str(uuid.uuid4()))
            chunks.append(chunk)
            metadatas.append({
                "source": doc["source"],
                "category": doc["category"],
            })

    if not chunks:
        return 0

    embeddings = embed_texts(chunks)
    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    return len(chunks)


# הפונקציה הבאה מממשת שלב מוגדר בתהליך העבודה של האפליקציה.
def retrieve_context(query: str, n_results: int = 4) -> tuple[str, list[str]]:
    chroma = get_chroma_client()
    collection = chroma.get_or_create_collection(name=COLLECTION_NAME)

    query_embedding = embed_texts([query])[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    context_lines = []
    sources = []
    for i, doc in enumerate(documents):
        source = metadatas[i].get("source", "unknown") if i < len(metadatas) else "unknown"
        sources.append(source)
        context_lines.append(f"[מקור: {source}]\n{doc}")

    return "\n\n".join(context_lines), sources
