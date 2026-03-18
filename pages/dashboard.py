import streamlit as st

from utils.navigation import render_sidebar

from utils.ocr_config import configure_ocr

configure_ocr()

from services.credit_service import get_user_credits

render_sidebar()

user = st.session_state.get("user")

st.title("📊 Dashboard")

user = st.session_state.get("user")

if not user:
    st.warning("Please login first")
    st.switch_page("app.py")  # or your login page
    st.stop()

# -----------------------------------
# USER INFO
# -----------------------------------

col1, col2 = st.columns([6, 2])

with col1:
    st.markdown(f"### Welcome back 👋")
    st.markdown(f"**User:** {user.email}")

with col2:
    st.image("assets/chumcred_logo.png", width=80)

st.divider()

# -----------------------------------
# KPI CARDS
# -----------------------------------

credits = 0

try:
    credits = get_user_credits(user.id)
except:
    credits = 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💰 Credits", credits)

with col2:
    st.metric("📄 Documents", "—")

with col3:
    st.metric("🤖 AI Queries", "—")

with col4:
    st.metric("📊 Status", "Active")

st.divider()

# -----------------------------------
# QUICK ACTIONS
# -----------------------------------

st.markdown("### 🚀 Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("💬 AI Chat", use_container_width=True, key="dash_ai_chat"):
        st.switch_page("pages/ai_chat.py")

with col2:
    if st.button("📄 PDF Tools", use_container_width=True, key="dash_pdf"):
        st.switch_page("pages/pdf_tools.py")

with col3:
    if st.button("🎞️ Media Tools", use_container_width=True, key="dash_media"):
        st.switch_page("pages/media_tools.py")

with col4:
    if st.button("📊 Financial Analyzer", use_container_width=True, key="dash_fin"):
        st.switch_page("pages/financial_analyzer.py")

st.divider()

# -----------------------------------
# INSIGHTS SECTION
# -----------------------------------

st.markdown("### 📈 Insights")

st.info("""
You can upload financial documents and let AI extract insights such as:
- Revenue trends
- Profitability
- Risk indicators
- Key financial ratios
""")

# -----------------------------------
# RECENT ACTIVITY (placeholder)
# -----------------------------------

st.markdown("### 🕘 Recent Activity")

st.write("No activity yet.")