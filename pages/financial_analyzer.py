import streamlit as st
from services.ai_service import summarize

from utils.ocr_config import configure_ocr
from utils.navigation import render_sidebar
from utils.feature_guard import enforce_feature_access, consume_feature_usage

configure_ocr()
render_sidebar()

user = enforce_feature_access("financial_analyzer")

st.title("AI Financial Document Analyzer")

uploaded_file = st.file_uploader(
    "Upload Financial Document",
    type=["txt", "pdf", "docx"]
)

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


if uploaded_file:

    text = extract_text(uploaded_file)

    if not text.strip():
        st.error("Could not extract text from document")
        st.stop()

    if st.button("Analyze Financials", key="financial_analyzer_btn"):

        consume_feature_usage("financial_analyzer")

        prompt = f"""
        Analyze this financial document and provide:

        1. Revenue insights
        2. Profitability assessment
        3. Debt and liquidity analysis
        4. Risk score (Low, Medium, High)
        5. Actionable recommendations

        Document:
        {text}
        """

        result = summarize(prompt)

        st.subheader("Financial Analysis")
        st.write(result)