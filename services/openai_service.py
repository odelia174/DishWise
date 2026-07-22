"""שירות משותף לעבודה עם OpenAI Responses API ויצירת תשובות."""
import os
from openai import OpenAI

SYSTEM_PROMPT = """
אתה DishWise, עוזר בישול ותזונה ידידותי.
ענה בעברית ברורה, מעשית ובטוחה.
הצע מתכונים לפי המצרכים, ההעדפות והאלרגיות שהמשתמש מציין.
כאשר קיים מידע מבסיס הידע, התבסס עליו וציין שהמידע מבוסס על המאגר.
אל תיתן אבחון רפואי ואל תקבע שמוצר בטוח לחלוטין לאלרגיים.
במקרה של אלרגיה או ספק, בקש לבדוק את האריזה המקורית ולהתייעץ עם איש מקצוע.
"""


# הפונקציה הבאה מממשת שלב מוגדר בתהליך העבודה של האפליקציה.
def get_client() -> OpenAI:
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# הפונקציה הבאה מממשת שלב מוגדר בתהליך העבודה של האפליקציה.
def get_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


# הפונקציה הבאה מממשת שלב מוגדר בתהליך העבודה של האפליקציה.
def extract_text(response) -> str:
    """Safely extract text from Responses API object."""
    if hasattr(response, "output_text") and response.output_text:
        return response.output_text

    texts = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if text:
                texts.append(text)
    return "\n".join(texts)


# הפונקציה הבאה מממשת שלב מוגדר בתהליך העבודה של האפליקציה.
def ask_dishwise(user_message: str, rag_context: str = "", image_summary: str = "") -> str:
    client = get_client()

    context_parts = []
    if rag_context:
        context_parts.append(f"מידע מבסיס הידע:\n{rag_context}")
    if image_summary:
        context_parts.append(f"מידע שזוהה מהתמונה:\n{image_summary}")

    full_prompt = user_message
    if context_parts:
        full_prompt = "\n\n".join(context_parts) + "\n\nשאלת המשתמש:\n" + user_message

    response = client.responses.create(
        model=get_model(),
        instructions=SYSTEM_PROMPT,
        input=full_prompt,
    )
    return extract_text(response)
