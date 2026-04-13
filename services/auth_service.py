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
            user_id = response.user.id

            existing = (
                supabase.table("users")
                .select("id")
                .eq("id", user_id)
                .execute()
            )

            if existing.data:
                (
                    supabase.table("users")
                    .update(
                        {
                            "email": email,
                            "full_name": full_name,
                            "role": "user",
                            "plan_code": "trial",
                        }
                    )
                    .eq("id", user_id)
                    .execute()
                )
            else:
                (
                    supabase.table("users")
                    .insert(
                        {
                            "id": user_id,
                            "email": email,
                            "full_name": full_name,
                            "role": "user",
                            "plan_code": "trial",
                        }
                    )
                    .execute()
                )

            create_default_trial_access(user_id, 14)

        return response

    except Exception as e:
        return {"error": str(e)}


def sign_in(email, password):
    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": email,
                "password": password
            }
        )
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