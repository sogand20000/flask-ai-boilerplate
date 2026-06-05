import os

from dotenv import load_dotenv
from flask import Blueprint, jsonify, request
from google import genai
from google.genai import errors, types
from supabase import Client, create_client
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

load_dotenv()

ai_bp = Blueprint("ai", __name__)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
)

try:
    ai_client = genai.Client()
except Exception as e:
    print(f"⚠️ Warning: Failed to initialize Gemini Client in blueprint: {e}")
    ai_client = None


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(errors.APIError),
    reraise=True,
)
def call_gemini_with_retry(client, history):
    return client.models.generate_content(model="gemini-2.5-flash", contents=history)


@ai_bp.route("/chat", methods=["POST"])
def chat():
    print("\n--- 🚀 [START] New Chat Request Received ---")
    try:
        data = request.get_json() or {}
        print(f"📥 1. Raw Data received from Frontend: {data}")
        user_message = data.get("message")
        chat_id = data.get("chat_id")
        print(
            f"🔍 2. Parsed Variables -> message: '{user_message}', chat_id: {chat_id} (Type: {type(chat_id)})"
        )
        if not user_message:
            print("⚠️ 3. Validation Failed: Message is empty!")
            return jsonify({"status": "error", "message": "Message is required"}), 400

        chat_history = []
        is_new_chat = True
        current_chat_id = None
        print("❓ 4. Checking if chat_id exists...")

        if chat_id is not None:
            print(f"🔍 4.1. chat_id: {chat_id} (Type: {type(chat_id)})")
            try:
                chat_id = int(chat_id)
                print(f"   -> Successfully converted chat_id to int: {chat_id}")
            except (ValueError, TypeError) as e:
                print(f"   ❌ 4a. Conversion Failed! Error: {str(e)}")
                return jsonify({"status": "error", "message": "Invalid chat_id"}), 401

            db_response = (
                supabase.table("chats").select("history").eq("id", chat_id).execute()
            )

            if db_response.data and len(db_response.data) > 0:
                db_record = db_response.data[0]
                chat_history = db_record.get("history", [])
                is_new_chat = False
                current_chat_id = chat_id

        chat_history.append({"role": "user", "parts": [user_message]})

        contents = []

        for msg in chat_history:
            contents.append(
                types.Content(
                    role=msg["role"],
                    parts=[
                        types.Part.from_text(
                            text=msg["parts"][0]
                            if isinstance(msg["parts"], list)
                            else msg["parts"]
                        )
                    ],
                )
            )

        config = types.GenerateContentConfig(
            system_instruction="You are an expert AI assistant. Provide concise, clear,"
            " and helpful answers."
        )
        print(f"🤖 Calling Gemini API...{contents}")
        gemini_response = call_gemini_with_retry(ai_client, contents)
        ai_response_text = gemini_response.text
        print("✨ Gemini Response Success!")
        chat_history.append({"role": "role", "parts": [ai_response_text]})

        if not is_new_chat and current_chat_id is not None:
            # آپدیت چت موجود

            supabase.table("chats").update({"history": chat_history}).eq(
                "id", current_chat_id
            ).execute()

        else:
            # ایجاد یک رکورد جدید و دریافت آی‌دی تولید شده توسط دیتابیس
            insert_response = (
                supabase.table("chats").insert({"history": chat_history}).execute()
            )
            if insert_response.data and len(insert_response.data) > 0:
                current_chat_id = insert_response.data[0]["id"]
            else:
                raise Exception("Supabase insert failed to return data.")

        return jsonify(
            {
                "chat_id": current_chat_id,
                "response": ai_response_text,
                "history": chat_history,
            }
        )
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": "An internal error occurred", "details": str(e)}), 500


@ai_bp.route("/chat/<int:chat_id>/history", methods=["GET"])
def get_chat_history(chat_id):
    try:
        print("\n--- 🚀 [START] New Chat Request Received --- {chat_id} ")
        db_response = (
            supabase.table("chats").select("history").eq("id", chat_id).execute()
        )
        if db_response.data and len(db_response.data) > 0:
            raw_history = db_response.data[0].get("history", [])

            formatted_messages = []
            for msg in raw_history:
                sender = "user" if msg["role"] == "user" else "ai"
                text = (
                    msg["parts"][0] if isinstance(msg["parts"], list) else msg["parts"]
                )
                formatted_messages.append({"sender": sender, "text": text})
            return jsonify({"status": "success", "messages": formatted_messages}), 200
        else:
            return jsonify({"status": "error", "message": "Chat not found"}), 404

    except Exception as e:
        return jsonify({"error": "Failed to fetch history", "details": str(e)}), 500
