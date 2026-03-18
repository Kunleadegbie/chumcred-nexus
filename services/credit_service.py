from services.supabase_client import supabase


def get_user_credits(user_id):

    response = (
        supabase.table("users")
        .select("credits_balance")
        .eq("id", user_id)
        .execute()
    )

    if not response.data:
        return 0  # fallback instead of crash

    return response.data[0]["credits_balance"]