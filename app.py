from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import uuid
import json

app = Flask(__name__)
app.secret_key = 'secret123'

USER_FILE = "users.txt"
TASK_FILE_PREFIX = "tasks_"
AVATAR_FOLDER = "static/avatars"
USER_AVATAR_MAP = "avatars"

app.config['UPLOAD_FOLDER'] = AVATAR_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(USER_AVATAR_MAP, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def task_file_path(username):
    return f"{TASK_FILE_PREFIX}{username}.json"

def load_tasks(username):
    try:
        with open(task_file_path(username), "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_tasks(username, tasks):
    with open(task_file_path(username), "w") as f:
        json.dump(tasks, f)

def register_user(username, password):
    with open(USER_FILE, "a") as f:
        f.write(f"{username}:{password}\n")

def verify_user(username, password):
    try:
        with open(USER_FILE, "r") as f:
            for line in f:
                stored_user, stored_pass = line.strip().split(":")
                if stored_user == username and stored_pass == password:
                    return True
    except FileNotFoundError:
        return False
    return False

@app.route("/", methods=["GET", "POST"])
def index():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    tasks = load_tasks(username)

    if request.method == "POST":
        if "add" in request.form:
            task_name = request.form.get("task", "").strip()
            priority = request.form.get("priority", "low")
            if task_name:
                tasks.append({
                    "id": str(uuid.uuid4()),
                    "name": task_name,
                    "priority": priority.lower()
                })
        elif "delete" in request.form:
            task_id = request.form.get("delete")
            tasks = [task for task in tasks if task["id"] != task_id]
        save_tasks(username, tasks)
        return redirect(url_for("index"))

    return render_template("index.html", tasks=tasks, user=username)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if verify_user(username, password):
            session["username"] = username
            return redirect(url_for("index"))
        else:
            return "Invalid login. Try again."
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        register_user(username, password)
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
