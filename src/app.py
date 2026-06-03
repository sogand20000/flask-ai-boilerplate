import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from src.routes.ai import ai_bp

# Load environment variables
load_dotenv()


basedir = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(basedir, ".env"))
frontend_folder = os.path.join(os.getcwd(), "frontend", "dist")
app = Flask(__name__, static_folder=frontend_folder, template_folder=frontend_folder)
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY", "fallback-secret-key-if-env-missing"
)
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:5177", "http://127.0.0.1:5177"],
)
app.register_blueprint(ai_bp, url_prefix="/api")

if __name__ == "__main__":
    app.run(debug=True)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


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
    port_env = os.getenv("PORT", "5000")
    port = int(port_env) if port_env.isdigit() else 5000
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"

    app.run(host="0.0.0.0", port=port, debug=debug_mode)
