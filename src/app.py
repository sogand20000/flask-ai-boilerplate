import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify
from src.routes.ai import ai_bp

# Load environment variables
load_dotenv()

app = Flask(__name__)

basedir = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(basedir, ".env"))

app = Flask(__name__)


app.register_blueprint(ai_bp, url_prefix="/api")


@app.route("/", methods=["GET"])
def index():
    return jsonify(
        {
            "status": "success",
            "message": "Flask AI Boilerplate API is running smoothly!",
        }
    ), 200


# Global Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify(
        {"status": "error", "message": "The requested URL was not found on the server."}
    ), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify(
        {"status": "error", "message": "An internal server error occurred."}
    ), 500


if __name__ == "__main__":
    # Dynamically read port and debug mode from environment variables
    port_env = os.getenv("PORT", "5001")
    port = int(port_env) if port_env.isdigit() else 5001
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"

    app.run(host="0.0.0.0", port=port, debug=debug_mode)
