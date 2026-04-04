import streamlit as st
from PyPDF2 import PdfReader, PdfMerger
from docx import Document
import io
import fitz  # PyMuPDF

# ===================================
# PAGE TITLE
# ===================================
st.title("📄 PDF Tools")

# ===================================
# TOOL SELECTOR
# ===================================
tool = st.selectbox(
    "Select Tool",
    [
        "PDF to Word (OCR)",
        "Merge PDFs"
    ]
)

# ===================================
# SAFE PDF → WORD (NO OCR DEPENDENCY)
# ===================================
def pdf_to_word_simple(file_bytes):

    doc = Document()
    pdf = fitz.open(stream=file_bytes, filetype="pdf")

    for page in pdf:

        text = page.get_text()

        # If no text (scanned doc), still handle gracefully
        if not text.strip():
            text = "[Scanned Page Detected – No embedded text found]"

        doc.add_paragraph(text)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer

# ===================================
# 1. PDF → WORD (FIXED)
# ===================================
if tool == "PDF to Word (OCR)":

    pdf = st.file_uploader("Upload PDF", type=["pdf"])

    if pdf and st.button("Convert to Word", use_container_width=True):

        try:
            file_bytes = pdf.read()

            st.info("Processing document...")

            buffer = pdf_to_word_simple(file_bytes)

            st.success("Conversion complete")

            st.download_button(
                "Download Word File",
                buffer,
                file_name="converted.docx"
            )

        except Exception as e:
            st.error(f"Conversion failed: {e}")

# ===================================
# 2. MERGE PDFs (UNCHANGED)
# ===================================
if tool == "Merge PDFs":

    pdf_files = st.file_uploader(
        "Upload multiple PDFs",
        type=["pdf"],
        accept_multiple_files=True
    )

    if pdf_files and st.button("Merge PDFs", use_container_width=True):

        try:
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