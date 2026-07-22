"""בניית בסיס הידע: טעינת מסמכים, יצירת Embeddings ושמירה ב-ChromaDB."""
from dotenv import load_dotenv
from services.rag_service import build_knowledge_base

if __name__ == "__main__":
    load_dotenv()
    count = build_knowledge_base("data")
    print(f"נוספו {count} קטעים לבסיס הידע של DishWise.")
