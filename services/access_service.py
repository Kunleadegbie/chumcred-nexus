from __future__ import annotations

from typing import Any, Optional

from services.supabase_client import supabase


def create_default_trial_access(user_id: str, trial_days: int = 14) -> Any:
    """
    Create a default trial access record for a new user.
    Trial days are clamped in SQL to 14-30.
    """
    return supabase.rpc(
        "create_default_access_control",
        {
            "p_user_id": user_id,
            "p_trial_days": trial_days,
        },
    ).execute()


def get_user_access_status(user_id: str) -> Optional[dict]:
    """
    Return access status row from SQL function.
    """
    response = supabase.rpc(
        "get_user_access_status",
        {"p_user_id": user_id},
    ).execute()

    if response.data:
        return response.data[0]
    return None


def check_and_increment_feature_usage(user_id: str, feature_name: str) -> Optional[dict]:
    """
    Enforce daily feature usage and increment if allowed.
    feature_name must match DB values:
    - ai_chat
    - ai_summary
    - financial_analyzer
    - ai_translate
    """
    response = supabase.rpc(
        "check_and_increment_feature_usage",
        {
            "p_user_id": user_id,
            "p_feature_name": feature_name,
        },
    ).execute()

    if response.data:
        return response.data[0]
    return None


def get_active_plans() -> list[dict]:
    response = (
        supabase.table("subscription_plans")
        .select("*")
        .eq("is_active", True)
        .order("amount")
        .execute()
    )
    return response.data or []


def create_subscription_request(user_id: str, requested_plan_code: str, request_note: str = "") -> Any:
    return (
        supabase.table("subscription_requests")
        .insert(
            {
                "user_id": user_id,
                "requested_plan_code": requested_plan_code,
                "request_note": request_note,
            }
        )
        .execute()
    )


def create_payment_record(
    user_id: str,
    amount: float,
    receipt_url: str,
    subscription_request_id: Optional[str] = None,
    payment_reference: str = "",
    payer_name: str = "",
    bank_name: str = "",
    payment_date: Optional[str] = None,
) -> Any:
    payload = {
        "user_id": user_id,
        "amount": amount,
        "receipt_url": receipt_url,
        "subscription_request_id": subscription_request_id,
        "payment_reference": payment_reference,
        "payer_name": payer_name,
        "bank_name": bank_name,
        "payment_date": payment_date,
        "payment_status": "pending",
    }

    return supabase.table("payments").insert(payload).execute()


def get_trial_banner_data(user_id: str) -> Optional[dict]:
    """
    Fetch user + access summary for dashboard/banner display.
    """
    response = (
        supabase.table("admin_user_overview")
        .select("*")
        .eq("id", user_id)
        .execute()
    )
    if response.data:
        return response.data[0]
    return None


def get_all_users_overview() -> list[dict]:
    response = (
        supabase.table("admin_user_overview")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []


def block_user(admin_user_id: str, target_user_id: str, reason: str = "") -> Any:
    return supabase.rpc(
        "block_user",
        {
            "p_admin_user_id": admin_user_id,
            "p_target_user_id": target_user_id,
            "p_reason": reason,
        },
    ).execute()


def unblock_user(admin_user_id: str, target_user_id: str, note: str = "") -> Any:
    return supabase.rpc(
        "unblock_user",
        {
            "p_admin_user_id": admin_user_id,
            "p_target_user_id": target_user_id,
            "p_note": note,
        },
    ).execute()


def set_trial_period(admin_user_id: str, target_user_id: str, trial_days: int) -> Any:
    return supabase.rpc(
        "set_trial_period",
        {
            "p_admin_user_id": admin_user_id,
            "p_target_user_id": target_user_id,
            "p_trial_days": trial_days,
        },
    ).execute()