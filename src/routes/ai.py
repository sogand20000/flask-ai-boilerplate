from flask import Blueprint, jsonify, request, session
from google import genai
from google.genai import errors
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
def generate_content_with_retry(client, history):
    return client.models.generate_content(model="gemini-2.5-flash", contents=history)


@ai_bp.route("/chat", methods=["POST"])
def chat():

    if "chat_history" not in session:
        session["chat_history"] = []

    if not ai_client:
        return jsonify(
            {
                "status": "error",
                "message": "Gemini Client is not initialized. Check your API key.",
            }
        ), 500

    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"status": "error", "message": "Message is required"}), 400

    new_user_turn = {"role": "user", "parts": [{"text": user_message}]}
    history = session["chat_history"]
    history.append(new_user_turn)
    session["chat_history"] = history

    try:
        response = generate_content_with_retry(ai_client, session["chat_history"])
        ai_response_text = response.text

        new_model_turn = {"role": "model", "parts": [{"text": ai_response_text}]}
        history = session["chat_history"]
        history.append(new_model_turn)
        session["chat_history"] = history

        return jsonify(
            {
                "status": "success",
                "data": {"user_message": user_message, "response": ai_response_text},
            }
        ), 200

    except errors.APIError as e:
        return jsonify(
            {"status": "error", "message": f"Gemini API Error: {e.message}"}
        ), e.code or 500
    except Exception as e:
        return jsonify(
            {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}
        ), 500
