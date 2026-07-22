"""שירות Vision: המרת תמונות ושליחתן לניתוח באמצעות OpenAI."""
import base64
import mimetypes
from pathlib import Path
from services.openai_service import get_client, get_model, extract_text


# הפונקציה הבאה מממשת שלב מוגדר בתהליך העבודה של האפליקציה.
def image_to_data_url(image_path: str) -> str:
    path = Path(image_path)
    mime_type = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"


# הפונקציה הבאה מממשת שלב מוגדר בתהליך העבודה של האפליקציה.
def analyze_image(image_path: str, mode: str) -> str:
    """Analyze fridge/pantry or food label image using Vision input."""
    client = get_client()
    data_url = image_to_data_url(image_path)

    if mode == "label":
        task = """
נתח את תמונת תווית המזון.
החזר:
1. שם מוצר אם ניתן לזהות.
2. רכיבים שמופיעים בתווית.
3. אלרגנים שמופיעים במפורש או חשודים.
4. ערכים תזונתיים מרכזיים.
5. הסבר קצר וברור למשתמש.
6. אזהרה: במקרה של אלרגיה חובה לבדוק את האריזה המקורית.
"""
    else:
        task = """
נתח את תמונת המקרר או המזווה.
החזר:
1. מצרכים שזוהו בוודאות.
2. פריטים שלא ברורים.
3. 3 רעיונות למתכונים מהמצרכים שזוהו.
4. אילו מוצרים חסרים לכל מתכון.
"""

    response = client.responses.create(
        model=get_model(),
        instructions="אתה עוזר בישול ותזונה. ענה בעברית בצורה זהירה ומעשית.",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": task},
                    {"type": "input_image", "image_url": data_url},
                ],
            }
        ],
    )
    return extract_text(response)
