import streamlit as st
from services.ai_service import translate

from utils.ocr_config import configure_ocr
from utils.navigation import render_sidebar
from utils.feature_guard import enforce_feature_access, consume_feature_usage

configure_ocr()
render_sidebar()

user = enforce_feature_access("ai_translate")

st.title("🌍 AI Translator")

languages = [
    "Auto Detect",
    "English",
    "French",
    "Spanish",
    "German",
    "Arabic",
    "Chinese",
    "Yoruba",
    "Hausa",
    "Igbo"
]

col1, col2 = st.columns(2)

with col1:
    source_lang = st.selectbox("From", languages, key="ai_translate_source")

with col2:
    target_lang = st.selectbox("To", languages[1:], key="ai_translate_target")

uploaded_file = st.file_uploader(
    "Upload Document (Optional)",
    type=["txt", "pdf", "docx"]
)

text_input = st.text_area("Or paste text manually", key="ai_translate_text")

def extract_text(file):
    if file.type == "text/plain":
        return file.read().decode("utf-8", errors="ignore")

    elif file.type == "application/pdf":
        from PyPDF2 import PdfReader
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        from docx import Document
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])

    return ""

final_text = ""

if uploaded_file:
    final_text = extract_text(uploaded_file)
elif text_input:
    final_text = text_input

if final_text:

    if st.button("Translate", key="ai_translate_btn"):

        consume_feature_usage("ai_translate")

        with st.spinner("Translating..."):
            if source_lang == "Auto Detect":
                prompt = f"Translate the following text to {target_lang}:\n\n{final_text}"
            else:
                prompt = f"Translate the following text from {source_lang} to {target_lang}:\n\n{final_text}"

            result = translate(prompt, target_lang)

        st.subheader("Translated Output")
        st.write(result)