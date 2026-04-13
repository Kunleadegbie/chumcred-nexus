import streamlit as st
from pdf2image import convert_from_bytes
import pytesseract
from PyPDF2 import PdfReader
from PIL import Image
import io
from openai import OpenAI
import os
import requests

from utils.ocr_config import configure_ocr
from utils.navigation import render_sidebar
from utils.feature_guard import enforce_feature_access, consume_feature_usage

# -----------------------------------
# CONFIG
# -----------------------------------
configure_ocr()
render_sidebar()

user = enforce_feature_access("ai_chat")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("💬 AI Document Chat (Pro)")

# -----------------------------------
# SESSION STATE
# -----------------------------------
if "doc_ready" not in st.session_state:
    st.session_state.doc_ready = False

if "chunks" not in st.session_state:
    st.session_state.chunks = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_loaded_file" not in st.session_state:
    st.session_state.last_loaded_file = None

# -----------------------------------
# FILE SOURCES (UPLOAD + VAULT)
# -----------------------------------
uploaded_file = st.file_uploader("Upload Document", type=["pdf", "jpg", "png"])

vault_url = st.session_state.get("vault_file_url")
vault_name = st.session_state.get("vault_file_name")

file_bytes = None
file_name = None
file_type = None

if uploaded_file:
    file_bytes = uploaded_file.read()
    file_name = uploaded_file.name
    file_type = uploaded_file.type
    st.success(f"Uploaded: {file_name}")

elif vault_url:
    try:
        response = requests.get(vault_url)
        file_bytes = response.content
        file_name = vault_name or "Vault File"
        file_type = "application/pdf"
        st.success(f"Loaded from Vault: {file_name}")
    except Exception as e:
        st.error(f"Failed to load file from Vault: {e}")

# -----------------------------------
# VALIDATE FILE
# -----------------------------------
if file_bytes:
    if file_type == "application/pdf" and not file_bytes.startswith(b"%PDF"):
        st.error("❌ Invalid PDF file from Vault")
        st.info("""
This means:
- The Vault URL is not returning a real PDF
- Likely a permissions or storage issue
        """)
        st.stop()
else:
    st.warning("Upload a file or select one from Vault")
    st.stop()

# -----------------------------------
# TEXT EXTRACTION
# -----------------------------------
def extract_text(file_bytes, file_type):
    text = ""

    if file_type == "application/pdf":
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                text += page.extract_text() or ""
        except Exception:
            pass

        if len(text.strip()) < 100:
            st.info("Using OCR fallback...")
            try:
                import platform

                if platform.system() == "Windows":
                    POPPLER_PATH = r"C:\Users\ADEGBIE ADEKUNLE\poppler\poppler-25.12.0\Library\bin"
                else:
                    POPPLER_PATH = None

                images = convert_from_bytes(
                    file_bytes,
                    dpi=300,
                    poppler_path=POPPLER_PATH
                )

                for img in images:
                    text += pytesseract.image_to_string(img)

            except Exception as e:
                st.warning("OCR fallback failed — continuing with available text")
                st.warning(str(e))

    else:
        try:
            image = Image.open(io.BytesIO(file_bytes))
            text = pytesseract.image_to_string(image)
        except Exception as e:
            st.error(f"Image OCR failed: {e}")

    return text

# -----------------------------------
# TEXT CHUNKING + RETRIEVAL
# -----------------------------------
def chunk_text(text, chunk_size=1000):
    words = text.split()
    return [
        " ".join(words[i:i + chunk_size])
        for i in range(0, len(words), chunk_size)
    ]


def get_relevant_chunks(chunks, question):
    scored = []

    for chunk in chunks:
        score = sum(
            1 for word in question.lower().split()
            if word in chunk.lower()
        )
        scored.append((score, chunk))

    scored.sort(reverse=True)

    return "\n\n".join(
        [chunk for score, chunk in scored[:3]]
    )

# -----------------------------------
# PROCESS DOCUMENT
# -----------------------------------
if file_bytes:

    if file_name != st.session_state.last_loaded_file:
        st.session_state.doc_ready = False
        st.session_state.chat_history = []

    if not st.session_state.doc_ready:

        if st.button("📄 Process Document", use_container_width=True, key="ai_chat_process_doc"):

            with st.spinner("Extracting document text..."):

                full_text = extract_text(file_bytes, file_type)

                if len(full_text.strip()) < 50:
                    st.error("Could not extract readable text.")
                    st.stop()

                st.session_state.chunks = chunk_text(full_text)
                st.session_state.doc_ready = True
                st.session_state.last_loaded_file = file_name

            st.success("Document processed successfully!")

# -----------------------------------
# CHAT SECTION
# -----------------------------------
if st.session_state.doc_ready:

    st.markdown("### Ask questions about your document")

    question = st.text_input("Enter your question", key="ai_chat_question")

    if st.button("🤖 Ask AI", use_container_width=True, key="ai_chat_ask_btn"):

        if not question:
            st.warning("Please enter a question")
            st.stop()

        consume_feature_usage("ai_chat")

        relevant_text = get_relevant_chunks(
            st.session_state.chunks,
            question
        )

        messages = [
            {"role": "system", "content": "You are a financial document analyst."}
        ]

        for q, a in st.session_state.chat_history:
            messages.append({"role": "user", "content": q})
            messages.append({"role": "assistant", "content": a})

        messages.append({
            "role": "user",
            "content": f"""
CONTEXT:
{relevant_text}

QUESTION:
{question}

INSTRUCTIONS:
- Extract exact figures
- Perform calculations if needed
- Reference where the answer comes from
- If not found, say "Not found in document"
"""
        })

        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )

        answer = response.choices[0].message.content
        st.session_state.chat_history.append((question, answer))

# -----------------------------------
# DISPLAY CHAT HISTORY
# -----------------------------------
if st.session_state.chat_history:

    st.markdown("### Conversation")

    for q, a in st.session_state.chat_history[::-1]:
        st.markdown(f"**🧑 You:** {q}")
        st.markdown(f"**🤖 AI:** {a}")
        st.divider()