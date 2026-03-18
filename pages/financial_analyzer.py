import streamlit as st
from services.ai_service import summarize

from utils.ocr_config import configure_ocr

configure_ocr()

from utils.navigation import render_sidebar

render_sidebar()

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

    if st.button("Analyze Financials"):

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