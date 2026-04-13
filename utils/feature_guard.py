import streamlit as st
from services.access_service import get_user_access_status, check_and_increment_feature_usage
from services.supabase_client import supabase


ADMIN_EMAILS = {
    "chumcred@gmail.com",
    "admin@chumcred.com",
}


def require_logged_in_user():
    user = st.session_state.get("user")
    if not user:
        st.warning("Please login first.")
        st.switch_page("app.py")
        st.stop()
    return user


def _is_admin_user(user) -> bool:
    email = getattr(user, "email", None)
    if email in ADMIN_EMAILS:
        return True

    try:
        response = (
            supabase.table("users")
            .select("role")
            .eq("id", user.id)
            .execute()
        )
        if response.data and response.data[0].get("role") == "admin":
            return True
    except Exception:
        pass

    return False


def enforce_feature_access(feature_name: str):
    user = require_logged_in_user()

    if _is_admin_user(user):
        return user

    access = get_user_access_status(user.id)
    if not access:
        st.error("Access record not found. Please contact admin.")
        st.stop()

    if not access.get("is_allowed", False):
        if access.get("is_blocked"):
            st.error("Your account has been blocked. Please contact admin.")
        elif access.get("subscription_status") == "expired":
            st.error("Your trial or subscription has expired. Please upgrade to continue.")
        else:
            st.error("Your access is currently restricted.")
        st.stop()

    return user


def consume_feature_usage(feature_name: str):
    user = require_logged_in_user()

    if _is_admin_user(user):
        return {
            "allowed": True,
            "usage_count": 0,
            "daily_limit": 999999,
            "message": "Admin bypass"
        }

    result = check_and_increment_feature_usage(user.id, feature_name)
    if not result:
        st.error("Could not verify usage limit.")
        st.stop()

    if not result.get("allowed", False):
        st.warning(
            f"{result.get('message', 'Daily limit reached')}. "
            f"Used: {result.get('usage_count', 0)} / {result.get('daily_limit', 0)}"
        )
        st.stop()

    return result