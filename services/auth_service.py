from services.supabase_client import supabase
from services.access_service import create_default_trial_access


def sign_up(email, password, full_name=""):

    response = supabase.auth.sign_up(
        {
            "email": email,
            "password": password
        }
    )

    if getattr(response, "user", None):

        # Upsert user profile into app users table
        supabase.table("users").upsert(
            {
                "id": response.user.id,
                "email": email,
                "full_name": full_name,
                "role": "user",
                "plan_code": "trial",
            }
        ).execute()

        # Create default trial access record
        create_default_trial_access(response.user.id, 14)

    return response


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

    supabase.auth.sign_out()