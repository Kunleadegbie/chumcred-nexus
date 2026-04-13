import streamlit as st

def render_sidebar():

    with st.sidebar:

        st.image("assets/chumcred_logo.png", width=120)
        st.markdown("## Chumcred Nexus")
        st.caption("AI Productivity Workspace")

        st.divider()

        # ===============================
        # CORE DASHBOARD
        # ===============================
        if st.button("🏠 Dashboard", use_container_width=True, key="nav_dashboard"):
            st.switch_page("pages/dashboard.py")

        st.divider()

        # ===============================
        # AI TOOLS
        # ===============================
        st.markdown("### 🤖 AI Tools")

        if st.button("💬 AI Chat", use_container_width=True, key="nav_ai_chat"):
            st.switch_page("pages/ai_chat.py")

        if st.button("📝 AI Summary", use_container_width=True, key="nav_ai_summary"):
            st.switch_page("pages/ai_summary.py")

        if st.button("🌍 AI Translate", use_container_width=True, key="nav_ai_translate"):
            st.switch_page("pages/ai_translate.py")

        if st.button("📊 Financial Analyzer", use_container_width=True, key="nav_fin"):
            st.switch_page("pages/financial_analyzer.py")

        st.divider()

        # ===============================
        # FILE TOOLS
        # ===============================
        st.markdown("### 📂 File Tools")

        if st.button("📄 PDF Tools", use_container_width=True, key="nav_pdf"):
            st.switch_page("pages/pdf_tools.py")

        if st.button("🎞️ Media Tools", use_container_width=True, key="nav_media"):
            st.switch_page("pages/media_tools.py")

        st.divider()

        # ===============================
        # STORAGE
        # ===============================
        st.markdown("### 🔐 Storage")

        if st.button("🗂️ Vault", use_container_width=True, key="nav_vault"):
            st.switch_page("pages/vault.py")

        st.divider()

        # ===============================
        # ACCOUNT
        # ===============================
        st.markdown("### ⚙️ Account")

        if st.button("💳 Subscription", use_container_width=True, key="nav_sub"):
            st.switch_page("pages/subscription.py")

        
        st.divider()
        st.markdown("### 🛠️ Admin")

        if st.button("🛠️ Admin Panel", use_container_width=True, key="nav_admin_panel"):
            st.switch_page("pages/admin.py")

        if st.button("💳 Subscription Approvals", use_container_width=True, key="nav_sub_approvals"):
            st.switch_page("pages/subscription_approvals.py")

        st.divider()
        if st.button("🚪 Logout", use_container_width=True, key="nav_logout"):
            st.session_state.clear()
            st.switch_page("app.py")