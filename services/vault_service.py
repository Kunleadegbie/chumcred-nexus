from services.supabase_client import supabase

def upload_to_vault(user_id, file_name, file_bytes):

    path = f"{user_id}/{file_name}"

    supabase.storage.from_("vault").upload(path, file_bytes)

    file_url = supabase.storage.from_("vault").get_public_url(path)

    return file_url