from flask import Blueprint, jsonify, request
from google import genai
from google.genai import errors, types
from backend.src.services.supabase_service import (
    get_chat_by_id,
    insert_new_chat_history,
    supabase,
    update_chat_history,
)
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

ai_bp = Blueprint("ai", __name__)


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
    try:
        data = request.get_json() or {}
        user_message = data.get("message")
        chat_id = data.get("chat_id")

        if not user_message:
            return jsonify({"status": "error", "message": "Message is required"}), 400

        chat_history = []
        is_new_chat = True
        current_chat_id = None

        if chat_id is not None:
            try:
                chat_id = int(chat_id)
            except (ValueError, TypeError) as e:
                return jsonify({"status": "error", "message": "Invalid chat_id"}), 401

            db_response = get_chat_by_id(chat_id)

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

        gemini_response = call_gemini_with_retry(ai_client, contents)
        ai_response_text = gemini_response.text
        chat_history.append({"role": "model", "parts": [ai_response_text]})

        if not is_new_chat and current_chat_id is not None:
            update_chat_history(current_chat_id, chat_history)

        else:
            insert_response = insert_new_chat_history(chat_history)

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
