import streamlit as st
from utils.navigation import render_sidebar
from services.supabase_client import upload_to_vault, list_vault_files
import pandas as pd

render_sidebar()

user = st.session_state.get("user")

# --------------------------------------
# SAFETY CHECK
# --------------------------------------
if not user:
    st.warning("Please login first")
    st.stop()

st.title("🗂️ Chumcred Vault")
st.caption("Secure Document Storage & Reuse")

# ======================================
# UPLOAD SECTION
# ======================================

st.markdown("### 📤 Upload Document")

col1, col2 = st.columns(2)

with col1:
    file = st.file_uploader("Choose file")

with col2:
    category = st.selectbox(
        "Category",
        ["General", "Financial", "Legal", "Personal"]
    )

if file and st.button("Upload to Vault", key="vault_upload"):
    try:
        file_url = upload_to_vault(
            user.id,
            file.name,
            file.read()
        )
        st.success("File uploaded successfully")
    except Exception as e:
        st.error(f"Upload failed: {e}")

# ======================================
# SEARCH + FILTER
# ======================================

st.divider()

st.markdown("### 🔍 Search Vault")

search = st.text_input("Search by file name")

try:
    files = list_vault_files(user.id)
except Exception as e:
    st.error(f"Error loading vault: {e}")
    files = []

if not files:
    st.info("No files in vault yet.")
    st.stop()

df = pd.DataFrame(files)

if search:
    df = df[df["file_name"].str.contains(search, case=False, na=False)]

# ======================================
# FILE LIST
# ======================================

st.markdown("### 📁 Your Files")

for i, row in df.iterrows():

    col1, col2, col3 = st.columns([6, 2, 2])

    with col1:
        st.markdown(f"**{row['file_name']}**")

    with col2:
        st.link_button("View", row["file_url"])

    with col3:
        st.download_button(
            "Download",
            data=row["file_url"],
            file_name=row["file_name"],
            key=f"download_{i}"
        )

# ======================================
# QUICK ACTIONS
# ======================================

st.divider()

st.markdown("### ⚡ Use File with AI")

file_list = df["file_name"].tolist()

if not file_list:
    st.warning("No files available for selection")
    st.stop()

selected_file = st.selectbox(
    "Select a file",
    file_list
)

if selected_file:

    selected_row = df[df["file_name"] == selected_file].iloc[0]

    file_url = selected_row["file_url"]
    file_name = selected_row["file_name"]

    st.success(f"Selected: {file_name}")

    col1, col2, col3 = st.columns(3)

    # AI CHAT
    with col1:
        if st.button("💬 Chat with Document", key="vault_chat"):
            st.session_state["vault_file_url"] = file_url
            st.session_state["vault_file_name"] = file_name
            st.switch_page("pages/ai_chat.py")

    # AI SUMMARY
    with col2:
        if st.button("📝 Summarize Document", key="vault_summary"):
            st.session_state["vault_file_url"] = file_url
            st.session_state["vault_file_name"] = file_name
            st.switch_page("pages/ai_summary.py")

    # FINANCIAL ANALYZER (NEW)
    with col3:
        if st.button("📊 Financial Analyzer", key="vault_fin"):
            st.session_state["vault_file_url"] = file_url
            st.session_state["vault_file_name"] = file_name
            st.switch_page("pages/financial_analyzer.py")