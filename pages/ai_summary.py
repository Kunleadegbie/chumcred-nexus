import streamlit as st
from services.ai_service import summarize

from utils.ocr_config import configure_ocr

configure_ocr()

from utils.navigation import render_sidebar

render_sidebar()

from utils.feature_guard import enforce_feature_access

user = enforce_feature_access("ai_chat")

st.title("AI Document Summarizer")

uploaded_file = st.file_uploader(
    "Upload Document",
    type=["txt", "pdf", "docx"]
)

from utils.feature_guard import consume_feature_usage

consume_feature_usage("ai_chat")

def extract_text(file):
    import io

    if file.type == "text/plain":
        return file.read().decode("utf-8", errors="ignore")

    elif file.type == "application/pdf":
        from PyPDF2 import PdfReader
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    elif file.type in [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]:
        from docx import Document
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])

    return ""


if uploaded_file:

    text = extract_text(uploaded_file)

    if not text.strip():
        st.error("Could not extract text from document")
        st.stop()

    st.success("Document loaded successfully")

    if st.button("Summarize Document"):

        with st.spinner("AI is summarizing..."):

            result = summarize(text)

        st.subheader("Summary")
        st.write(result)