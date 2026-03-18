import streamlit as st
import io
from pdf2image import convert_from_bytes
import pytesseract
from docx import Document
from PyPDF2 import PdfMerger
from PIL import Image

from utils.ocr_config import configure_ocr

configure_ocr()

from utils.navigation import render_sidebar

render_sidebar()

st.title("📄 PDF & Document Tools")

# -----------------------------------
# CONFIG (IMPORTANT FOR OCR)
# -----------------------------------

# For local Windows (optional)
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\Users\ADEGBIE ADEKUNLE\poppler\poppler-25.12.0\Library\bin"

# Uncomment if running locally
# pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# -----------------------------------
# TOOL SELECTOR
# -----------------------------------

tool = st.selectbox(
    "Select Tool",
    [
        "PDF to Word (OCR)",
        "Merge PDFs",
        "Images to PDF"
    ]
)

# ===================================
# 1. PDF → WORD (OCR)
# ===================================

if tool == "PDF to Word (OCR)":

    pdf = st.file_uploader("Upload PDF", type=["pdf"])

    if pdf and st.button("Convert to Word"):

        try:
            pages = convert_from_bytes(
                pdf.read(),
                dpi=300,
                poppler_path=POPPLER_PATH  # ignored in cloud
            )

            doc = Document()

            progress = st.progress(0)

            for i, page in enumerate(pages):
                text = pytesseract.image_to_string(page)
                doc.add_paragraph(text)

                progress.progress((i + 1) / len(pages))

            buffer = io.BytesIO()
            doc.save(buffer)

            st.success("Conversion complete")

            st.download_button(
                "Download Word File",
                buffer.getvalue(),
                file_name="converted.docx"
            )

        except Exception as e:
            st.error(f"OCR failed: {e}")

# ===================================
# 2. MERGE PDFs
# ===================================

elif tool == "Merge PDFs":

    files = st.file_uploader(
        "Upload multiple PDFs",
        type=["pdf"],
        accept_multiple_files=True
    )

    if files and st.button("Merge PDFs"):

        try:
            merger = PdfMerger()

            for f in files:
                merger.append(io.BytesIO(f.read()))

            buffer = io.BytesIO()
            merger.write(buffer)
            merger.close()

            st.success("Merge complete")

            st.download_button(
                "Download Merged PDF",
                buffer.getvalue(),
                file_name="merged.pdf"
            )

        except Exception as e:
            st.error(f"Merge failed: {e}")

# ===================================
# 3. IMAGES → PDF
# ===================================

elif tool == "Images to PDF":

    images = st.file_uploader(
        "Upload Images",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    if images and st.button("Convert to PDF"):

        try:
            pil_images = []

            for img_file in images:
                image = Image.open(img_file).convert("RGB")
                pil_images.append(image)

            buffer = io.BytesIO()

            pil_images[0].save(
                buffer,
                save_all=True,
                append_images=pil_images[1:]
            )

            st.success("Conversion complete")

            st.download_button(
                "Download PDF",
                buffer.getvalue(),
                file_name="images.pdf"
            )

        except Exception as e:
            st.error(f"Conversion failed: {e}")