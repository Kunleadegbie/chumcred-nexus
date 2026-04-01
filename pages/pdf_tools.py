import streamlit as st
import io
from pdf2image import convert_from_bytes
import pytesseract
from docx import Document
from PyPDF2 import PdfMerger
from PIL import Image

from pptx import Presentation
from PyPDF2 import PdfReader
import subprocess
import tempfile
import os

import pytesseract

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

import os
st.write("Tesseract exists:", os.path.exists("/usr/bin/tesseract"))

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
            file_bytes = pdf.read()

            doc = Document()
            progress = st.progress(0)

            # STEP 1: Try OCR (with Poppler)
            try:
                pages = convert_from_bytes(
                    file_bytes,
                    dpi=300,
                )

                for i, page in enumerate(pages):
                    text = pytesseract.image_to_string(page)
                    doc.add_paragraph(text)

                    progress.progress((i + 1) / len(pages))

            # STEP 2: FALLBACK (if Poppler fails)
            except Exception as ocr_error:
                st.warning("OCR not available — switching to basic extraction")

            
                reader = PdfReader(io.BytesIO(file_bytes))

                for i, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    doc.add_paragraph(text)

                    progress.progress((i + 1) / len(reader.pages))

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
            

            # 🚨 ADD THIS BLOCK HERE
            if len(doc.paragraphs) == 0:
                st.error("This document appears to be scanned and OCR is not available.")
                st.info("Please enable OCR (Poppler + Tesseract) or upload a text-based PDF.")
                st.stop()

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

# ===================================
# 4. PDF → POWERPOINT
# ===================================

def pdf_to_ppt(file_bytes):
    reader = PdfReader(io.BytesIO(file_bytes))
    prs = Presentation()

    for page in reader.pages:
        text = page.extract_text() or ""

        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)

        title = slide.shapes.title
        content = slide.placeholders[1]

        title.text = "Extracted Content"
        content.text = text[:1000]

    ppt_bytes = io.BytesIO()
    prs.save(ppt_bytes)
    ppt_bytes.seek(0)

    return ppt_bytes

# ===================================
# 5. POWERPOINT → PDF
# ===================================
def ppt_to_pdf(file):
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, file.name)

        with open(input_path, "wb") as f:
            f.write(file.read())

        subprocess.run([
            "soffice",
            "--headless",
            "--convert-to",
            "pdf",
            input_path,
            "--outdir",
            tmpdir
        ])

        output_file = input_path.replace(".pptx", ".pdf")

        with open(output_file, "rb") as f:
            return f.read()


st.divider()
st.subheader("📄 PDF ↔ PowerPoint")

col1, col2 = st.columns(2)

# PDF → PPT
with col1:
    pdf_file = st.file_uploader("PDF to PPT", type=["pdf"], key="pdf_to_ppt")

    if pdf_file and st.button("Convert to PPT", key="btn_pdf_to_ppt", use_container_width=True):
        ppt_file = pdf_to_ppt(pdf_file.read())

        st.download_button(
            "Download PPT",
            ppt_file,
            file_name="converted.pptx"
        )

# PPT → PDF
with col2:
    ppt_file = st.file_uploader("PPT to PDF", type=["pptx"], key="ppt_to_pdf")

    if ppt_file and st.button("Convert to PDF", key="btn_ppt_to_pdf", use_container_width=True):
        pdf_bytes = ppt_to_pdf(ppt_file)

        st.download_button(
            "Download PDF",
            pdf_bytes,
            file_name="converted.pdf"
        )
