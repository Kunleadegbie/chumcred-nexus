import streamlit as st
import tempfile
import subprocess
import os
from PIL import Image
import io


from utils.ocr_config import configure_ocr

configure_ocr()

from utils.navigation import render_sidebar

render_sidebar()

st.title("🎞️ Media Compression Tools")

# ======================================
# HELPER FUNCTIONS
# ======================================

def get_size_mb(file_bytes):
    return round(len(file_bytes) / (1024 * 1024), 2)


# --------------------------------------
# IMAGE COMPRESSION
# --------------------------------------

def compress_image(uploaded_file, quality):
    image = Image.open(uploaded_file).convert("RGB")

    buffer = io.BytesIO()

    image.save(
        buffer,
        format="JPEG",
        quality=quality,
        optimize=True
    )

    return buffer.getvalue()


# --------------------------------------
# VIDEO COMPRESSION (FFmpeg)
# --------------------------------------

def compress_video(input_bytes, crf_value):

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as input_file:
        input_file.write(input_bytes)
        input_path = input_file.name

    output_path = input_path.replace(".mp4", "_compressed.mp4")

    command = [
        "ffmpeg",
        "-i", input_path,
        "-vcodec", "libx264",
        "-crf", str(crf_value),
        "-preset", "fast",
        output_path
    ]

    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    with open(output_path, "rb") as f:
        output_bytes = f.read()

    os.remove(input_path)
    os.remove(output_path)

    return output_bytes


# --------------------------------------
# PDF COMPRESSION (Ghostscript)
# --------------------------------------

def compress_pdf(input_bytes, setting):

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as input_file:
        input_file.write(input_bytes)
        input_path = input_file.name

    output_path = input_path.replace(".pdf", "_compressed.pdf")

    command = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS=/{setting}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        input_path
    ]

    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    with open(output_path, "rb") as f:
        output_bytes = f.read()

    os.remove(input_path)
    os.remove(output_path)

    return output_bytes


# ======================================
# UI SELECTOR
# ======================================

tool = st.selectbox(
    "Select Tool",
    [
        "Image Compressor",
        "Video Compressor",
        "PDF Compressor"
    ]
)

# ======================================
# IMAGE COMPRESSOR
# ======================================

if tool == "Image Compressor":

    file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    level = st.selectbox("Compression Level", ["Low", "Medium", "High"])

    quality_map = {
        "Low": 85,
        "Medium": 60,
        "High": 40
    }

    if file and st.button("Compress Image"):

        compressed = compress_image(file, quality_map[level])

        st.success("Compression complete")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Original Size (MB)", get_size_mb(file.read()))

        with col2:
            st.metric("Compressed Size (MB)", get_size_mb(compressed))

        st.download_button(
            "Download Image",
            compressed,
            file_name="compressed.jpg"
        )

# ======================================
# VIDEO COMPRESSOR
# ======================================

elif tool == "Video Compressor":

    file = st.file_uploader("Upload Video", type=["mp4", "mov", "avi"])

    level = st.selectbox("Compression Level", ["Low", "Medium", "High"])

    crf_map = {
        "Low": 23,
        "Medium": 28,
        "High": 32
    }

    if file and st.button("Compress Video"):

        with st.spinner("Processing video..."):

            compressed = compress_video(file.read(), crf_map[level])

        st.success("Compression complete")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Original Size (MB)", get_size_mb(file.read()))

        with col2:
            st.metric("Compressed Size (MB)", get_size_mb(compressed))

        st.download_button(
            "Download Video",
            compressed,
            file_name="compressed.mp4"
        )

# ======================================
# PDF COMPRESSOR
# ======================================

elif tool == "PDF Compressor":

    file = st.file_uploader("Upload PDF", type=["pdf"])

    level = st.selectbox("Compression Level", ["Low", "Medium", "High"])

    pdf_map = {
        "Low": "printer",
        "Medium": "ebook",
        "High": "screen"
    }

    if file and st.button("Compress PDF"):

        with st.spinner("Compressing PDF..."):

            compressed = compress_pdf(file.read(), pdf_map[level])

        st.success("Compression complete")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Original Size (MB)", get_size_mb(file.read()))

        with col2:
            st.metric("Compressed Size (MB)", get_size_mb(compressed))

        st.download_button(
            "Download PDF",
            compressed,
            file_name="compressed.pdf"
        )

# ======================================
# MERGE IMAGES
# ======================================
def merge_images_to_pdf(uploaded_files):
    images = []

    for file in uploaded_files:
        image = Image.open(file).convert("RGB")
        images.append(image)

    pdf_bytes = io.BytesIO()

    images[0].save(
        pdf_bytes,
        format="PDF",
        save_all=True,
        append_images=images[1:]
    )

    pdf_bytes.seek(0)
    return pdf_bytes

st.divider()
st.subheader("🖼️ Merge Images")

image_files = st.file_uploader(
    "Upload images",
    type=["jpg", "png"],
    accept_multiple_files=True
)

if image_files and st.button("Merge to PDF", use_container_width=True):

    pdf_file = merge_images_to_pdf(image_files)

    st.success("Images merged successfully!")

    st.download_button(
        "Download PDF",
        pdf_file,
        file_name="merged_images.pdf",
        mime="application/pdf"
    )