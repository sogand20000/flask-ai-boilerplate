from flask import Blueprint, jsonify, request
from google import genai
from google.genai import errors

ai_bp = Blueprint("ai", __name__)

try:
    ai_client = genai.Client()
except Exception as e:
    print(f"⚠️ Warning: Failed to initialize Gemini Client in blueprint: {e}")
    ai_client = None


@ai_bp.route("/chat", methods=["POST"])
def chat():
    if not ai_client:
        return jsonify(
            {
                "status": "error",
                "message": "Gemini Client is not initialized. Check your API key.",
            }
        ), 500

    data = request.get_json()
    if not data or "prompt" not in data:
        return jsonify(
            {
                "status": "error",
                "message": "Missing required field: 'prompt' in request body.",
            }
        ), 400

    user_prompt = data["prompt"]

    try:
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt,
        )

        return jsonify(
            {
                "status": "success",
                "data": {"prompt": user_prompt, "response": response.text},
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
