from flask import Flask, jsonify, request, url_for

app = Flask(__name__)

PROJECTS_DB = {
    1: {"name": "AI Agent for Email Automation", "status": "active"},
    2: {"name": "RAG System for Legal Documents", "status": "draft"},
}


@app.route("/project/<int:project_id>", methods=["GET"])
def get_project(project_id):
    project = PROJECTS_DB.get(project_id)
    if not project:
        return jsonify(
            {"error": "Not Found", "message": f"Project {project_id} does not exist"}
        ), 404
    return jsonify({"project_id": project_id, "data": project}), 200


@app.route("/api/process", methods=["POST"])
def process_data():
    if request.is_json:
        data = request.get_json()
        user_prompt = data.get("prompt") if data else None
    else:
        user_prompt = request.form.get("prompt")

    if not user_prompt:
        return (
            jsonify({"error": "Bad Request", "message": "Missing 'prompt' in data"}),
            400,
        )

    return (
        jsonify(
            {
                "status": "success",
                "method_used": "POST",
                "ai_response": f"Processed: {user_prompt[::-1]}",
            }
        ),
        200,
    )


@app.route("/", methods=["GET"])
def home():
    project_url = url_for("get_project", project_id=1)
    process_url = url_for("process_data")

    return (
        f"<h2>Welcome to Flask AI Boilerplate!</h2>"
        f"<p>1. Test dynamic routing (GET): "
        f"<a href='{project_url}'>{project_url}</a></p>"
        f"<hr>"
        f"<p>2. Test AI Processing (POST) directly from here:</p>"
        f"<form action='{process_url}' method='POST' style='margin-top: 10px;'>"
        f"<textarea name='prompt' rows='3' cols='40' "
        f"placeholder='Type your prompt here...' required>"
        f"</textarea><br><br>"
        f"  <button type='submit'>Send POST Request to AI</button>"
        f"</form>"
    )


@app.route("/api/test", methods=["GET", "POST"])
def test_modes():
    if request.method == "GET":
        name = request.args.get("name", "Guest")
        return jsonify({"message": f"Hello {name}, this is a Get requset"}), 200
    elif request.method == "POST":
        data = request.get_json()
        role = data.get("role", "User") if data else "User"
        return jsonify({"message": f"Role '{role} updated via POST request !"}), 201


@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Resource not found", "status": 404}), 404


@app.errorhandler(500)
def internal_server_error(error):
    return (
        jsonify(
            {
                "status": "error",
                "error_code": 500,
                "message": "An unexpected error occurred inside the Python backend.",
            }
        ),
        500,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5002)
