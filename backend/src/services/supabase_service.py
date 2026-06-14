import os
from dotenv import load_dotenv
from supabase import Client, create_client
from backend.src.services.rag_service import get_embedding

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print(
        "⚠️ Warning: Supabase client not initialized. "
        "Check SUPABASE_URL and SUPABASE_KEY in .env file."
    )
    supabase = None
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


def insert_document(content: str, metadata: dict = None):
    if supabase is None:
        print("❌ Supabase client is not initialized!")
        return False

    try:
        chunks = chunk_text_smart(content, chunk_size=1000, overlap=200)
        print(f"📦 [RAG] Text split into {len(chunks)} chunks.")

        success_all = True

        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)

            if not embedding:
                print(f"❌ Failed to generate embedding for chunk #{i+1}")
                success_all = False
                continue

            chunk_metadata = (metadata or {}).copy()
            chunk_metadata["chunk_index"] = i   
            chunk_metadata["total_chunks"] = len(chunks)

            data = {
                "content": chunk,
                "metadata": chunk_metadata,
                "embedding": embedding,
            }

            response = supabase.table("documents").insert(data).execute()

            if response.data and len(response.data) > 0:
                print(f"✅ Chunk #{i+1}/{len(chunks)} successfully saved to Supabase! ID: {response.data[0]['id']}")
            else:
                success_all = False

        return success_all

    except Exception as e:
        print(f"❌ Error inserting document to Supabase: {e}")
        return False


def chunk_text_smart(text: str, chunk_size: int = 1000, overlap: int = 200) -> list:
    chunks = []
    raw_paragraphs = text.split("\n")
    current_chunk = ""

    for para in raw_paragraphs:
        if not para.strip():
            continue
        if len(current_chunk) + len(para) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())

            overlap_start = max(0, len(current_chunk) - overlap)    
            current_chunk = current_chunk[overlap_start:] + "\n" + para
        else:
            if current_chunk:
                current_chunk += "\n" + para
            else:
                current_chunk = para       

    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks