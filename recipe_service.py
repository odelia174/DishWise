"""יצירת מתכונים מובנים בפורמט JSON באמצעות Structured Outputs."""
import json
from services.openai_service import get_client, get_model, extract_text

RECIPE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "recipe_name": {"type": "string"},
        "short_description": {"type": "string"},
        "preparation_time_minutes": {"type": "integer"},
        "servings": {"type": "integer"},
        "ingredients": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "quantity": {"type": "string"},
                    "already_available": {"type": "boolean"}
                },
                "required": ["name", "quantity", "already_available"]
            }
        },
        "instructions": {"type": "array", "items": {"type": "string"}},
        "possible_allergens": {"type": "array", "items": {"type": "string"}},
        "shopping_list": {"type": "array", "items": {"type": "string"}},
        "nutrition_note": {"type": "string"},
        "safety_note": {"type": "string"}
    },
    "required": [
        "recipe_name",
        "short_description",
        "preparation_time_minutes",
        "servings",
        "ingredients",
        "instructions",
        "possible_allergens",
        "shopping_list",
        "nutrition_note",
        "safety_note"
    ]
}


# הפונקציה הבאה מממשת שלב מוגדר בתהליך העבודה של האפליקציה.
def create_structured_recipe(user_request: str, available_items: str = "", rag_context: str = "") -> dict:
    client = get_client()

    prompt = f"""
צור מתכון מותאם אישית בעברית לפי הבקשה.
בקשת המשתמש:
{user_request}

מצרכים זמינים:
{available_items}

מידע רלוונטי מבסיס הידע:
{rag_context}

החזר JSON בלבד לפי הסכמה.
"""

    response = client.responses.create(
        model=get_model(),
        instructions="אתה DishWise. החזר מתכון בטוח, מעשי ומובנה בעברית.",
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "dishwise_recipe",
                "schema": RECIPE_SCHEMA,
                "strict": True,
            }
        },
    )

    text = extract_text(response)
    return json.loads(text)
