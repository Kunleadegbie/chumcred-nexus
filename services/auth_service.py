from services.supabase_client import supabase
from services.access_service import create_default_trial_access


def sign_up(email, password, full_name=""):
    try:
        response = supabase.auth.sign_up(
            {
                "email": email,
                "password": password
            }
        )

        if getattr(response, "user", None):
            supabase.table("users").upsert(
                {
                    "id": response.user.id,
                    "email": email,
                    "full_name": full_name,
                    "role": "user",
                    "plan_code": "trial",
                },
                on_conflict="id"
            ).execute()

            create_default_trial_access(response.user.id, 14)

        return response

    except Exception as e:
        return {"error": str(e)}


def sign_up(email, password, full_name=""):
    try:
        response = supabase.auth.sign_up(
            {
                "email": email,
                "password": password
            }
        )

        if getattr(response, "user", None):
            supabase.table("users").upsert(
                {
                    "id": response.user.id,
                    "email": email,
                    "full_name": full_name,
                    "role": "user",
                    "plan_code": "trial",
                },
                on_conflict="id"
            ).execute()

            create_default_trial_access(response.user.id, 14)

        return response

    except Exception as e:
        return {"error": str(e)}


def get_current_user(session):
    if session is None:
        return None
    return session.user


def sign_out():
    try:
        supabase.auth.sign_out()
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}