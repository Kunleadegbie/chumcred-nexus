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

            # check if app user row already exists
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