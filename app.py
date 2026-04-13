import streamlit as st
from services.auth_service import sign_in, sign_up
from services.user_service import ensure_user_exists

st.set_page_config(
    page_title="Chumcred Nexus",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------
# SESSION STATE
# -----------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if "has_seen_about" not in st.session_state:
    st.session_state.has_seen_about = False

# -----------------------------------
# HEADER
# -----------------------------------
def render_login_header():
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("assets/chumcred_logo.png", width=80)
    with col2:
        st.title("Chumcred Nexus")
        st.caption("AI Productivity Workspace")

# -----------------------------------
# SIDEBAR (ONLY AFTER LOGIN)
# -----------------------------------
def render_sidebar():
    with st.sidebar:
        st.image("assets/chumcred_logo.png", width=120)
        st.markdown("## Chumcred Nexus")
        st.caption("AI Productivity Workspace")
        st.divider()

        st.page_link("pages/dashboard.py", label="Dashboard", icon="🏠")
        st.page_link("pages/ai_chat.py", label="AI Chat", icon="💬")
        st.page_link("pages/ai_translate.py", label="AI Translate", icon="🌍")
        st.page_link("pages/financial_analyzer.py", label="Financial Analyzer", icon="📊")
        st.page_link("pages/pdf_tools.py", label="PDF Tools", icon="📄")
        st.page_link("pages/media_tools.py", label="Media Tools", icon="🎞️")
        st.page_link("pages/subscription.py", label="Subscription", icon="💳")

        st.divider()

        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.switch_page("app.py")

# -----------------------------------
# ABOUT / LANDING PAGE
# -----------------------------------
def render_about_page():

    st.markdown("""
    <style>
    .hero {
        text-align: center;
        padding: 40px 20px;
    }
    .hero h1 {
        font-size: 42px;
        font-weight: 700;
    }
    .hero p {
        font-size: 18px;
        color: #555;
    }
    .card {
        padding: 20px;
        border-radius: 12px;
        background-color: #f8f9fb;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .pricing {
        border-radius: 12px;
        padding: 20px;
        background: #ffffff;
        box-shadow: 0 3px 15px rgba(0,0,0,0.08);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero">
        <h1>🚀 Chumcred Nexus</h1>
        <p>The AI-Powered Productivity & Intelligence Workspace</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="card">💬 <b>AI Document Chat</b><br>Ask questions directly from your files.</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">📊 <b>Financial Analysis</b><br>Extract insights from financial statements instantly.</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="card">🌍 <b>AI Translation</b><br>Translate languages intelligently both ways.</div>', unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown('<div class="card">🧠 <b>AI Summarization</b><br>Turn long documents into concise insights.</div>', unsafe_allow_html=True)

    with col5:
        st.markdown('<div class="card">🗂️ <b>Smart Vault</b><br>Store, reuse and connect files to AI tools.</div>', unsafe_allow_html=True)

    with col6:
        st.markdown('<div class="card">🎞️ <b>Media Tools</b><br>Compress and optimize images, videos, PDFs.</div>', unsafe_allow_html=True)

    st.divider()

    st.subheader("🎯 Who is Nexus for?")

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown("✔ Business Analysts")
    col2.markdown("✔ Financial Professionals")
    col3.markdown("✔ Entrepreneurs")
    col4.markdown("✔ Students & Researchers")

    st.divider()

    st.subheader("⚡ Why Chumcred Nexus?")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        - Save hours of manual work  
        - Automate repetitive tasks  
        - Extract insights instantly  
        """)

    with col2:
        st.markdown("""
        - Improve decision making  
        - Scale productivity  
        - Work smarter with AI  
        """)

    st.divider()

    st.subheader("💰 Pricing Plans")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="pricing">
        <h3>Starter</h3>
        <p>Basic AI tools</p>
        <p>Limited access during trial</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="pricing">
        <h3>Pro</h3>
        <p>Full AI access</p>
        <p>Higher limits</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="pricing">
        <h3>Premium</h3>
        <p>Unlimited usage</p>
        <p>Priority AI performance</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### 🚀 Ready to get started?")

    if st.button("👉 Go to Login / Create Account", use_container_width=True):
        st.session_state.has_seen_about = True
        st.rerun()

# -----------------------------------
# LOGIN PAGE
# -----------------------------------
def render_login_page():

    render_login_header()

    st.markdown("### Login to continue")
    mode = st.radio("", ["Login", "Register"], horizontal=True, key="auth_mode")

    if mode == "Login":
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", use_container_width=True, key="login_btn"):

            session = sign_in(email, password)

            if isinstance(session, dict) and "error" in session:
                st.error(session["error"])

            elif session and getattr(session, "user", None):
                st.session_state["user"] = session.user
                ensure_user_exists(session.user)
                st.switch_page("pages/dashboard.py")

            else:
                st.error("Invalid login")

    else:
        full_name = st.text_input("Full Name", key="register_full_name")
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")

        if st.button("Create Account", use_container_width=True, key="register_btn"):

            if len(password) < 6:
                st.error("Password must be at least 6 characters.")
                st.stop()

            res = sign_up(email, password, full_name)

            if isinstance(res, dict) and "error" in res:
                st.error(res["error"])

            elif res and getattr(res, "user", None):
                st.success(
                    "Account created successfully. Please check your email and click the confirmation link before logging in."
                )
                st.info("If you do not see the email, check your spam or junk folder.")


            else:
                st.error("Signup failed")


# -----------------------------------
# MAIN FLOW CONTROL
# -----------------------------------
user = st.session_state.get("user")

if user:
    render_sidebar()
    st.switch_page("pages/dashboard.py")

else:
    if not st.session_state.has_seen_about:
        render_about_page()
        st.stop()
    else:
        render_login_page()
        st.stop()