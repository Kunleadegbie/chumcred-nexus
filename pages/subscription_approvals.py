import streamlit as st
import pandas as pd

from utils.navigation import render_sidebar
from utils.feature_guard import require_logged_in_user, is_admin_user
from services.supabase_client import supabase

render_sidebar()

user = require_logged_in_user()

# -----------------------------------
# ADMIN GUARD
# -----------------------------------
if not is_admin_user(user):
    st.error("Access denied. Admin only.")
    st.stop()

st.title("💳 Subscription Approval Page")
st.caption("Review payment uploads and approve paid subscriptions")

# -----------------------------------
# HELPERS
# -----------------------------------
def get_pending_payments():
    try:
        response = (
            supabase.table("payments")
            .select(
                """
                id,
                user_id,
                subscription_request_id,
                amount,
                payment_reference,
                payer_name,
                bank_name,
                payment_date,
                receipt_url,
                payment_status,
                admin_note,
                approved_by,
                approved_at,
                created_at
                """
            )
            .eq("payment_status", "pending")
            .order("created_at", desc=True)
            .execute()
        )
        return response.data or []
    except Exception as e:
        st.error(f"Failed to load pending payments: {e}")
        return []


def get_all_plans():
    try:
        response = (
            supabase.table("subscription_plans")
            .select("plan_code, plan_name, amount, billing_cycle")
            .eq("is_active", True)
            .order("amount")
            .execute()
        )
        return response.data or []
    except Exception as e:
        st.error(f"Failed to load plans: {e}")
        return []


def get_user_info(user_id: str):
    try:
        response = (
            supabase.table("users")
            .select("id, full_name, email, plan_code")
            .eq("id", user_id)
            .execute()
        )
        if response.data:
            return response.data[0]
        return None
    except Exception:
        return None


def approve_payment_and_activate_plan(payment_id: str, plan_code: str, admin_note: str = ""):
    try:
        payment_response = (
            supabase.table("payments")
            .select("id, user_id, subscription_request_id")
            .eq("id", payment_id)
            .single()
            .execute()
        )

        payment = payment_response.data
        if not payment:
            return False, "Payment record not found."

        target_user_id = payment["user_id"]
        subscription_request_id = payment.get("subscription_request_id")

        (
            supabase.table("payments")
            .update(
                {
                    "payment_status": "approved",
                    "admin_note": admin_note,
                    "approved_by": user.id,
                    "approved_at": "now()",
                }
            )
            .eq("id", payment_id)
            .execute()
        )

        if subscription_request_id:
            (
                supabase.table("subscription_requests")
                .update(
                    {
                        "request_status": "approved",
                        "reviewed_by": user.id,
                        "reviewed_at": "now()",
                    }
                )
                .eq("id", subscription_request_id)
                .execute()
            )

        (
            supabase.table("users")
            .update({"plan_code": plan_code})
            .eq("id", target_user_id)
            .execute()
        )

        (
            supabase.table("user_access_control")
            .update(
                {
                    "subscription_status": "active_paid",
                    "access_status": "active",
                    "is_blocked": False,
                    "block_reason": None,
                }
            )
            .eq("user_id", target_user_id)
            .execute()
        )

        supabase.table("admin_actions").insert(
            {
                "admin_user_id": user.id,
                "target_user_id": target_user_id,
                "action_type": "approve_payment",
                "action_note": f"Activated plan: {plan_code}. {admin_note}".strip(),
            }
        ).execute()

        return True, "Payment approved and subscription activated."

    except Exception as e:
        return False, str(e)


def reject_payment(payment_id: str, admin_note: str = ""):
    try:
        payment_response = (
            supabase.table("payments")
            .select("id, user_id, subscription_request_id")
            .eq("id", payment_id)
            .single()
            .execute()
        )

        payment = payment_response.data
        if not payment:
            return False, "Payment record not found."

        target_user_id = payment["user_id"]
        subscription_request_id = payment.get("subscription_request_id")

        (
            supabase.table("payments")
            .update(
                {
                    "payment_status": "rejected",
                    "admin_note": admin_note,
                    "approved_by": user.id,
                    "approved_at": "now()",
                }
            )
            .eq("id", payment_id)
            .execute()
        )

        if subscription_request_id:
            (
                supabase.table("subscription_requests")
                .update(
                    {
                        "request_status": "rejected",
                        "reviewed_by": user.id,
                        "reviewed_at": "now()",
                    }
                )
                .eq("id", subscription_request_id)
                .execute()
            )

        supabase.table("admin_actions").insert(
            {
                "admin_user_id": user.id,
                "target_user_id": target_user_id,
                "action_type": "reject_payment",
                "action_note": admin_note or "Payment rejected",
            }
        ).execute()

        return True, "Payment rejected successfully."

    except Exception as e:
        return False, str(e)


# -----------------------------------
# LOAD DATA
# -----------------------------------
pending_payments = get_pending_payments()
plans = get_all_plans()

if not plans:
    st.warning("No active subscription plans found.")
    st.stop()

plan_options = {
    f"{p['plan_name']} ({p['plan_code']}) - ₦{int(p['amount'])}/{p['billing_cycle']}": p["plan_code"]
    for p in plans
}

# -----------------------------------
# SUMMARY
# -----------------------------------
col1, col2 = st.columns(2)

with col1:
    st.metric("Pending Payments", len(pending_payments))

with col2:
    st.metric("Active Plans", len(plans))

st.divider()

# -----------------------------------
# PAYMENT TABLE
# -----------------------------------
st.subheader("Pending Subscription Payments")

if not pending_payments:
    st.info("No pending payments at the moment.")
    st.stop()

display_rows = []
for p in pending_payments:
    user_info = get_user_info(p["user_id"]) or {}
    display_rows.append(
        {
            "payment_id": p["id"],
            "name": user_info.get("full_name"),
            "email": user_info.get("email"),
            "current_plan": user_info.get("plan_code"),
            "amount": p.get("amount"),
            "payer_name": p.get("payer_name"),
            "bank_name": p.get("bank_name"),
            "payment_reference": p.get("payment_reference"),
            "payment_date": p.get("payment_date"),
            "receipt_url": p.get("receipt_url"),
            "created_at": p.get("created_at"),
        }
    )

df = pd.DataFrame(display_rows)
st.dataframe(df, use_container_width=True)

st.divider()

# -----------------------------------
# REVIEW PANEL
# -----------------------------------
st.subheader("Review a Payment")

payment_labels = []
payment_lookup = {}

for row in display_rows:
    label = f"{row.get('name') or 'No Name'} | {row.get('email') or 'No Email'} | ₦{row.get('amount')}"
    payment_labels.append(label)
    payment_lookup[label] = row

selected_label = st.selectbox("Select payment", payment_labels, key="sub_approval_select")
selected_payment = payment_lookup[selected_label]

st.markdown(f"**User:** {selected_payment.get('name') or 'No Name'}")
st.markdown(f"**Email:** {selected_payment.get('email') or 'No Email'}")
st.markdown(f"**Current Plan:** {selected_payment.get('current_plan')}")
st.markdown(f"**Amount Paid:** ₦{selected_payment.get('amount')}")
st.markdown(f"**Payer Name:** {selected_payment.get('payer_name') or '-'}")
st.markdown(f"**Bank Name:** {selected_payment.get('bank_name') or '-'}")
st.markdown(f"**Payment Reference:** {selected_payment.get('payment_reference') or '-'}")
st.markdown(f"**Payment Date:** {selected_payment.get('payment_date') or '-'}")

receipt_url = selected_payment.get("receipt_url")
if receipt_url:
    st.link_button("Open Receipt", receipt_url)

selected_plan_label = st.selectbox("Assign plan after approval", list(plan_options.keys()), key="sub_approval_plan")
selected_plan_code = plan_options[selected_plan_label]

admin_note = st.text_area("Admin note", key="payment_admin_note")

col1, col2 = st.columns(2)

with col1:
    if st.button("✅ Approve Payment", use_container_width=True, key="approve_payment_btn"):
        success, message = approve_payment_and_activate_plan(
            payment_id=selected_payment["payment_id"],
            plan_code=selected_plan_code,
            admin_note=admin_note,
        )
        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)

with col2:
    if st.button("❌ Reject Payment", use_container_width=True, key="reject_payment_btn"):
        success, message = reject_payment(
            payment_id=selected_payment["payment_id"],
            admin_note=admin_note,
        )
        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)