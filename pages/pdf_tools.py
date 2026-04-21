import streamlit as st
from PyPDF2 import PdfMerger
from docx import Document
import io
import fitz  # PyMuPDF
from PIL import Image
import os
import easyocr
import numpy as np


from utils.navigation import render_sidebar

render_sidebar()

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
# SAFE PDF → WORD WITH OCR FALLBACK
# ===================================
def pdf_to_word_with_ocr(file_bytes):
    doc = Document()
    pdf = fitz.open(stream=file_bytes, filetype="pdf")

    reader = easyocr.Reader(["en"], gpu=False)

    total_pages = len(pdf)
    progress = st.progress(0)

    for page_number, page in enumerate(pdf, start=1):
        text = page.get_text("text").strip()

        if not text:
            try:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_bytes = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                image_np = np.array(image)

                results = reader.readtext(image_np, detail=0, paragraph=True)
                text = "\n".join(results).strip()

            except Exception as e:
                text = f"[OCR failed on page {page_number}: {e}]"

        if not text:
            text = f"[No readable text could be extracted from page {page_number}]"

        doc.add_paragraph(text)
        progress.progress(page_number / total_pages)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer

# ===================================
# 1. PDF → WORD
# ===================================
if tool == "PDF to Word (OCR)":

    pdf = st.file_uploader("Upload PDF", type=["pdf"], key="pdf_to_word_uploader")

    if pdf and st.button("Convert to Word", use_container_width=True, key="pdf_to_word_btn"):

        try:
            file_bytes = pdf.read()

            st.info("Processing document...")

            buffer = pdf_to_word_with_ocr(file_bytes)

            st.success("Conversion complete")

            st.download_button(
                "Download Word File",
                buffer.getvalue(),
                file_name="converted.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="download_word_file"
            )

        except Exception as e:
            st.error(f"Conversion failed: {e}")

# ===================================
# 2. MERGE PDFs
# ===================================
if tool == "Merge PDFs":

    pdf_files = st.file_uploader(
        "Upload multiple PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        key="merge_pdfs_uploader"
    )

    if pdf_files and st.button("Merge PDFs", use_container_width=True, key="merge_pdfs_btn"):

        try:
            merger = PdfMerger()

            for pdf in pdf_files:
                merger.append(pdf)

            buffer = io.BytesIO()
            merger.write(buffer)
            merger.close()
            buffer.seek(0)

            st.success("PDFs merged successfully")

            st.download_button(
                "Download Merged PDF",
                buffer.getvalue(),
                file_name="merged.pdf",
                mime="application/pdf",
                key="download_merged_pdf"
            )

        except Exception as e:
            st.error(f"Merge failed: {e}")