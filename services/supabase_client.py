import os
from supabase import create_client
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ======================================
# VAULT STORAGE
# ======================================

def upload_to_vault(user_id, file_name, file_bytes):

    path = f"{user_id}/{file_name}"

    # Upload to storage bucket "vault"
    supabase.storage.from_("vault").upload(path, file_bytes)

    file_url = supabase.storage.from_("vault").get_public_url(path)

    # Save metadata in DB
    data = {
        "user_id": user_id,
        "file_name": file_name,
        "file_url": file_url,
        "file_type": file_name.split(".")[-1],
        "created_at": datetime.utcnow().isoformat()
    }

    supabase.table("vault_files").insert(data).execute()

    return file_url


def list_vault_files(user_id):

    response = (
        supabase.table("vault_files")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )

    return response.data