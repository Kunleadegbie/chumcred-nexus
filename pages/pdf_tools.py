import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
import io
import os

from openai import OpenAI

# ===============================
# CONFIG
# ===============================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("📄 PDF Tools")

# ===============================
# TOOL SELECTOR
# ===============================
tool = st.selectbox(
    "Select Tool",
    [
        "PDF to Word (AI)",
        "Merge PDFs"
    ]
)

# ===============================
# AI TEXT EXTRACTION (NO OCR)
# ===============================
def ai_extract_text(file_bytes):

    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Extract all readable text from this document clearly. Preserve structure where possible."
                        },
                        {
                            "type": "input_file",
                            "file_bytes": file_bytes
                        }
                    ]
                }
            ]
        )

        return response.output_text

    except Exception as e:
        return f"AI extraction failed: {e}"

# ===============================
# 1. PDF → WORD (AI POWERED)
# ===============================
if tool == "PDF to Word (AI)":

    pdf = st.file_uploader("Upload PDF", type=["pdf"])

    if pdf and st.button("Convert to Word", use_container_width=True):

        try:
            file_bytes = pdf.read()

            st.info("Processing document using AI...")

            text = ai_extract_text(file_bytes)

            if not text or len(text.strip()) < 20:
                st.error("Could not extract meaningful content from this document.")
                st.stop()

            doc = Document()

            for line in text.split("\n"):
                doc.add_paragraph(line)

            buffer = io.BytesIO()
            doc.save(buffer)

            st.success("Conversion complete")

            st.download_button(
                "Download Word File",
                buffer.getvalue(),
                file_name="converted.docx"
            )

        except Exception as e:
            st.error(f"Conversion failed: {e}")

# ===============================
# 2. MERGE PDFs
# ===============================
if tool == "Merge PDFs":

    pdf_files = st.file_uploader(
        "Upload multiple PDFs",
        type=["pdf"],
        accept_multiple_files=True
    )

    if pdf_files and st.button("Merge PDFs", use_container_width=True):

        try:
            from PyPDF2 import PdfMerger

            merger = PdfMerger()

            for pdf in pdf_files:
                merger.append(pdf)

            buffer = io.BytesIO()
            merger.write(buffer)
            merger.close()

            st.success("PDFs merged successfully")

            st.download_button(
                "Download Merged PDF",
                buffer.getvalue(),
                file_name="merged.pdf"
            )

        except Exception as e:
            st.error(f"Merge failed: {e}")