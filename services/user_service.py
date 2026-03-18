from services.supabase_client import supabase
try:
    from services.user_service import ensure_user_exists
except:
    ensure_user_exists = None

def ensure_user_exists(user):

    if not user:
        return

    response = (
        supabase.table("users")
        .select("*")
        .eq("id", user.id)
        .execute()
    )

    # If user not found, create it
    if not response.data:

        supabase.table("users").insert({
            "id": user.id,
            "email": user.email,
            "role": "user",
            "plan": "starter",
            "credits_balance": 20
        }).execute()