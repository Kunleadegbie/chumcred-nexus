from services.supabase_client import supabase

from services.supabase_client import supabase


def sign_up(email, password):

    response = supabase.auth.sign_up({
        "email": email,
        "password": password
    })

    if response.user:

        # Insert into users table
        supabase.table("users").insert({
            "id": response.user.id,
            "email": email,
            "role": "user",
            "plan": "starter",
            "credits_balance": 20
        }).execute()

    return response


from services.supabase_client import supabase


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