"""این ماژول یک سرور ساده فلاسک را برای شروع پروژه راه‌اندازی می‌کند."""

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


@app.route("/")
def home():
    """این تابع صفحه اصلی سایت را مدیریت کرده و پیام سلام بازمی‌گرداند."""
    return "<h1>سلام! سرور فلاسک من روی ابر با موفقیت روشن شد! 🚀</h1>"


@app.route("/welcome")
def welcom():
    "welcom"
    return render_template("index.html")


@app.route("/api/info")
def get_info():
    "return information in json file"
    data = {
        "project_name": "flask ai project",
        "status": "Active",
        "version": "1.0.0",
        "features": ["flask server", "pep8 com", "json api"],
    }
    return jsonify(data)


@app.route("/api/greet", methods=["GET", "POST"])
def greet_user():
    """این مسیر بر اساس متد ارسالی و پارامترها، پاسخ سفارشی تولید می‌کند."""
    if request.method == "POST":
        data = request.json
        if not isinstance(data, dict):
            data = {}
        name = data.get("name", "کاربر ناشناس")
        return jsonify(message=f"سلام {name}! درخواست POST شما با موفقیت دریافت شد.")
    name = request.args.get("name", "مهمان")
    return jsonify(message=f"سلام {name}! این یک پاسخ GET است.")


@app.route("/book/<string:isbn>")
def get_book(isbn):
    "example"
    return f"you can see {isbn} book"


@app.route("/post/<username>")
def show_user_profile(username):
    """این مسیر نام کاربری را از آدرس می‌گیرد و پیام خوش‌آمدگویی می‌فرستد."""
    return jsonify(user=username, message=f"wellcome {username}")


@app.route("/post/<int:post_id>")
def show_post(post_id):
    """این مسیر فقط عدد صحیح قبول می‌کند و شناسه پست را برمی‌گرداند."""
    return jsonify(post_id=post_id, status=" show maghaleh")


@app.route("/api/item/", defaults={"item_id": None})
@app.route("/api/item/<int:item_id>")
def get_item(item_id):
    "check id item"
    if item_id is None:
        return jsonify(error="please add id in address api/item/5"), 400

    if item_id > 10:
        return jsonify(error="dont exist item .."), 404
    return jsonify(item_id=item_id, status="find item")


@app.errorhandler(404)
def page_not_found():
    "errorhandler"
    return jsonify(error="dont exist item", code=404), 404


if __name__ == "__main__":
    app.run(debug=True, port=8080)
