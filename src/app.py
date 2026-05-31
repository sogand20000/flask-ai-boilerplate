import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from google import genai
from google.genai import errors

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize the Gemini Client
# It automatically reads GEMINI_API_KEY from the environment
try:
    ai_client = genai.Client()
except Exception as e:
    print(f"⚠️ Warning: Failed to initialize Gemini Client: {e}")
    ai_client = None


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "success",
        "message": "Flask AI Boilerplate API is running smoothly!"
    }), 200


# New Route for Gemini Chat Integration
@app.route("/api/chat", methods=["POST"])
def chat():
    # 1. Ensure the Gemini Client is properly initialized
    if not ai_client:
        return jsonify({
            "status": "error",
            "message": "Gemini Client is not initialized. Check your API key."
        }), 500

    # 2. Get and validate JSON data from the request
    data = request.get_json()
    if not data or "prompt" not in data:
        return jsonify({
            "status": "error",
            "message": "Missing required field: 'prompt' in request body."
        }), 400

    user_prompt = data["prompt"]

    try:
        # 3. Call Gemini 2.5 Flash model
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt,
        )

        # 4. Return the successful response
        return jsonify({
            "status": "success",
            "data": {
                "prompt": user_prompt,
                "response": response.text
            }
        }), 200

    except errors.APIError as e:
        # Handle specific Gemini API errors (e.g., quota exceeded, invalid key)
        return jsonify({
            "status": "error",
            "message": f"Gemini API Error: {e.message}"
        }), e.code or 500
    except Exception as e:
        # Handle general unexpected errors
        return jsonify({
            "status": "error",
            "message": f"An unexpected error occurred: {str(e)}"
        }), 500


# Global Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        "status": "error",
        "message": "The requested URL was not found on the server."
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "status": "error",
        "message": "An internal server error occurred."
    }), 500


if __name__ == "__main__":
    # Dynamically read port and debug mode from environment variables
    port_env = os.getenv("PORT", "5001")
    port = int(port_env) if port_env.isdigit() else 5001
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"

    app.run(host="0.0.0.0", port=port, debug=debug_mode)