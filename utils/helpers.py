import re
import io
from docx import Document


def sanitize_filename(name):

    name = re.sub(r"[^\w\-. ]+", "_", name)

    return name


def build_docx_from_text(text):

    doc = Document()

    paragraphs = text.split("\n")

    for p in paragraphs:
        doc.add_paragraph(p)

    buffer = io.BytesIO()

    doc.save(buffer)

    return buffer.getvalue()