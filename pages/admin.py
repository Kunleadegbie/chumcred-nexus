import streamlit as st
import pandas as pd

from utils.navigation import render_sidebar
from utils.feature_guard import require_logged_in_user
from services.access_service import (
    get_all_users_overview,
    block_user,
    unblock_user,
    set_trial_period,
)

render_sidebar()

user = require_logged_in_user()

# -----------------------------------
# ADMIN GUARD
# -----------------------------------
if getattr(user, "email", None) != "admin@chumcred.com":
    st.error("Access denied. Admin only.")
    st.stop()

st.title("🛠️ Admin Control Panel")
st.caption("Manage users, trial periods, and access control")

# -----------------------------------
# LOAD USERS
# -----------------------------------
def load_users():
    try:
        return get_all_users_overview()
    except Exception as e:
        st.error(f"Failed to load users: {e}")
        return []

users_data = load_users()

if not users_data:
    st.info("No users found.")
    st.stop()

df = pd.DataFrame(users_data)

# -----------------------------------
# SUMMARY METRICS
# -----------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Users", len(df))

with col2:
    active_count = int((df["access_status"] == "active").sum()) if "access_status" in df.columns else 0
    st.metric("Active Users", active_count)

with col3:
    blocked_count = int(df["is_blocked"].fillna(False).sum()) if "is_blocked" in df.columns else 0
    st.metric("Blocked Users", blocked_count)

with col4:
    trial_count = int((df["plan_code"] == "trial").sum()) if "plan_code" in df.columns else 0
    st.metric("Trial Users", trial_count)

st.divider()

# -----------------------------------
# USER TABLE
# -----------------------------------
st.subheader("All Users")

display_cols = [
    col for col in [
        "full_name",
        "email",
        "role",
        "plan_code",
        "access_status",
        "is_blocked",
        "trial_start_date",
        "trial_end_date",
        "trial_days",
        "subscription_status",
        "usage_today",
        "created_at",
        "last_login_at",
        "id",
    ]
    if col in df.columns
]

st.dataframe(df[display_cols], use_container_width=True)

st.divider()

# -----------------------------------
# USER ACTIONS
# -----------------------------------
st.subheader("User Actions")

user_options = [
    f"{row.get('full_name') or 'No Name'} | {row.get('email')} | {row.get('id')}"
    for _, row in df.iterrows()
]

selected_label = st.selectbox("Select user", user_options)

selected_row = df.iloc[user_options.index(selected_label)]
target_user_id = selected_row["id"]
target_email = selected_row.get("email", "")
target_name = selected_row.get("full_name", "No Name")
is_currently_blocked = bool(selected_row.get("is_blocked", False))

st.markdown(f"**Selected User:** {target_name} ({target_email})")

tab1, tab2, tab3 = st.tabs(["Block / Unblock", "Trial Period", "Refresh"])

# -----------------------------------
# BLOCK / UNBLOCK TAB
# -----------------------------------
with tab1:
    reason = st.text_area("Admin note / reason", key="admin_reason")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚫 Block User", use_container_width=True, key="block_user_btn"):
            try:
                block_user(user.id, target_user_id, reason)
                st.success("User blocked successfully.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to block user: {e}")

    with col2:
        if st.button("✅ Unblock User", use_container_width=True, key="unblock_user_btn"):
            try:
                unblock_user(user.id, target_user_id, reason)
                st.success("User unblocked successfully.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to unblock user: {e}")

    st.info(
        f"Current status: {'Blocked' if is_currently_blocked else 'Active'}"
    )

# -----------------------------------
# TRIAL PERIOD TAB
# -----------------------------------
with tab2:
    trial_days = st.number_input(
        "Set trial period (days)",
        min_value=14,
        max_value=30,
        value=int(selected_row.get("trial_days", 14) or 14),
        step=1,
        key="trial_days_input",
    )

    if st.button("⏳ Reset / Set Trial Period", use_container_width=True, key="set_trial_btn"):
        try:
            set_trial_period(user.id, target_user_id, int(trial_days))
            st.success(f"Trial set to {trial_days} days successfully.")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to set trial period: {e}")

# -----------------------------------
# REFRESH TAB
# -----------------------------------
with tab3:
    if st.button("🔄 Reload Users", use_container_width=True, key="reload_users_btn"):
        st.rerun()