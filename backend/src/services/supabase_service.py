import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")


if not SUPABASE_URL or not SUPABASE_KEY:
    print(
        "⚠️ Warning: Supabase client not initialized. "
        "Check SUPABASE_URL and SUPABASE_KEY"
        " in ."
        "env file."
    )
else:
    supabase: Client = create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
    )


def get_chat_by_id(chat_id: int):

    if not supabase:
        print("❌ Supabase client is not initialized!")
        return None

    try:
        db_response = (
            supabase.table("chats").select("history").eq("id", chat_id).execute()
        )
        return db_response
    except Exception as e:
        print(f"Error initializing Supabase client: {e}")
        return None


def update_chat_history(chat_id: int, chat_history: list):

    if not supabase:
        print("❌ Supabase client is not initialized!")
        return None
    try:
        supabase.table("chats").update({"history": chat_history}).eq(
            "id", chat_id
        ).execute()
    except Exception as e:
        print(f"Error updating chat history: {e}")
        return None


def insert_new_chat_history(chat_history: list):

    if not supabase:
        print("❌ Supabase client is not initialized!")
        return None
    try:
        insert_response = (
            supabase.table("chats").insert({"history": chat_history}).execute()
        )
        return insert_response
    except Exception as e:
        print(f"Error inserting new chat history: {e}")
        return None
