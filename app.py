"""ממשק Streamlit הראשי של DishWise: צ׳אט, Vision, RAG ומתכון מובנה."""
import os
import tempfile
import streamlit as st
from dotenv import load_dotenv

from services.openai_service import ask_dishwise
from services.vision_service import analyze_image
from services.rag_service import retrieve_context
from services.recipe_service import create_structured_recipe

load_dotenv()

st.set_page_config(page_title="DishWise", page_icon="🍽️", layout="wide")

st.title("🍽️ DishWise – עוזר תזונה, קניות ובישול מותאם אישית")
st.caption("מידע כללי בלבד. במקרה של אלרגיה או מצב רפואי, חובה לבדוק תוויות מקוריות ולהתייעץ עם איש מקצוע.")

if not os.getenv("OPENAI_API_KEY"):
    st.error("חסר OPENAI_API_KEY. צרו קובץ .env לפי .env.example")
    st.stop()

with st.sidebar:
    st.header("העדפות משתמש")
    diet = st.multiselect(
        "העדפות / מגבלות",
        ["צמחוני", "טבעוני", "ללא גלוטן", "ללא לקטוז", "דל סוכר", "דל מלח", "אלרגיה לבוטנים", "אלרגיה לאגוזים"]
    )
    max_time = st.slider("זמן הכנה מקסימלי בדקות", 10, 90, 30)
    servings = st.number_input("מספר מנות", min_value=1, max_value=10, value=2)

preferences = f"העדפות: {', '.join(diet) if diet else 'אין'}; זמן מקסימלי: {max_time} דקות; מנות: {servings}"

tab_chat, tab_image, tab_rag, tab_recipe = st.tabs([
    "💬 שיחה עם העוזר",
    "📷 ניתוח תמונה",
    "📚 שאלת RAG",
    "🧾 מתכון מובנה"
])

with tab_chat:
    st.subheader("שיחה חופשית עם DishWise")
    user_message = st.text_area("מה תרצו לשאול?", placeholder="יש לי ביצים, עגבניות וגבינה. מה אפשר להכין?")
    use_rag = st.checkbox("לשלב מידע מבסיס הידע", value=True)

    if st.button("שלח", key="chat_send"):
        with st.spinner("DishWise חושב..."):
            rag_context = ""
            if use_rag:
                rag_context, sources = retrieve_context(user_message)
            answer = ask_dishwise(user_message + "\n" + preferences, rag_context=rag_context)
            st.markdown(answer)

with tab_image:
    st.subheader("ניתוח מקרר/מזווה או תווית מזון")
    mode_label = st.radio("סוג הניתוח", ["מקרר/מזווה", "תווית מזון"])
    uploaded = st.file_uploader("העלו תמונה", type=["png", "jpg", "jpeg", "webp"])

    if uploaded:
        st.image(uploaded, caption="התמונה שהועלתה", use_container_width=True)

    if uploaded and st.button("נתח תמונה", key="image_analyze"):
        suffix = "." + uploaded.name.split(".")[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded.getvalue())
            temp_path = tmp.name

        with st.spinner("מנתח את התמונה..."):
            mode = "label" if mode_label == "תווית מזון" else "fridge"
            summary = analyze_image(temp_path, mode)
            st.session_state["last_image_summary"] = summary
            st.markdown(summary)

with tab_rag:
    st.subheader("שאלה המבוססת על בסיס הידע")
    rag_question = st.text_input("שאלת RAG", placeholder="לפי מדריך התחליפים, במה אפשר להחליף ביצה באפייה?")

    if st.button("חפש וענה", key="rag_send"):
        with st.spinner("מחפש ב-ChromaDB..."):
            context, sources = retrieve_context(rag_question)
            answer = ask_dishwise(rag_question + "\n" + preferences, rag_context=context)
            st.markdown(answer)
            with st.expander("מקורות שנשלפו"):
                for src in sources:
                    st.write(src)

with tab_recipe:
    st.subheader("יצירת מתכון מובנה עם Structured Outputs")
    request = st.text_area("בקשה למתכון", placeholder="צור מתכון טבעוני מהיר עם אורז, עדשים ועגבניות.")
    available_items = st.text_input("מצרכים זמינים", value=st.session_state.get("last_image_summary", ""))

    if st.button("צור מתכון מובנה", key="recipe_send"):
        with st.spinner("יוצר מתכון מובנה..."):
            context, _ = retrieve_context(request)
            recipe = create_structured_recipe(request + "\n" + preferences, available_items, context)

            st.success(recipe["recipe_name"])
            st.write(recipe["short_description"])
            st.write(f"⏱️ זמן הכנה: {recipe['preparation_time_minutes']} דקות | 🍽️ מנות: {recipe['servings']}")

            st.markdown("### רכיבים")
            for item in recipe["ingredients"]:
                status = "✅ יש בבית" if item["already_available"] else "🛒 לקנות"
                st.write(f"- {item['quantity']} {item['name']} — {status}")

            st.markdown("### שלבי הכנה")
            for i, step in enumerate(recipe["instructions"], start=1):
                st.write(f"{i}. {step}")

            st.markdown("### רשימת קניות")
            for item in recipe["shopping_list"]:
                st.checkbox(item, key=f"shop_{item}")

            st.markdown("### אלרגנים והערות")
            st.write(", ".join(recipe["possible_allergens"]) or "לא זוהו")
            st.info(recipe["nutrition_note"])
            st.warning(recipe["safety_note"])

            with st.expander("JSON מלא"):
                st.json(recipe)
