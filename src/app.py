import os, json, uuid, datetime
from flask import Flask, jsonify, request, render_template, send_from_directory
from storage import load_recipes, save_recipes
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder="templates")
DATA_PATH = os.environ.get("DATA_PATH", "data")
RECIPES_FILE = os.path.join(DATA_PATH, "recipes.json")

# Ensure data directory exists
os.makedirs(DATA_PATH, exist_ok=True)
if not os.path.exists(RECIPES_FILE):
    save_recipes([], RECIPES_FILE)

# Upload config
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    recipes = load_recipes(RECIPES_FILE)
    return render_template("index.html", recipes=recipes)

@app.route("/api/recipes", methods=["GET"])
def list_recipes():
    return jsonify(load_recipes(RECIPES_FILE)), 200

@app.route("/api/recipes", methods=["POST"])
def create_recipe():
    body = request.json
    if not body or "title" not in body:
        return jsonify({"ok": False, "error": "Missing title"}), 400
    recipe = {
        "id": str(uuid.uuid4()),
        "title": body["title"],
        "ingredients": body.get("ingredients", []),
        "steps": body.get("steps", []),
        "image_url": body.get("image_url", ""),
        "created_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    recipes = load_recipes(RECIPES_FILE)
    recipes.append(recipe)
    save_recipes(recipes, RECIPES_FILE)
    return jsonify({"ok": True, "recipe": recipe}), 201

@app.route("/api/recipes/<rid>", methods=["GET"])
def get_recipe(rid):
    recipes = load_recipes(RECIPES_FILE)
    for r in recipes:
        if r["id"] == rid:
            return jsonify(r), 200
    return jsonify({"ok": False, "error": "Not found"}), 404

@app.route("/api/recipes/<rid>", methods=["PATCH"])
def update_recipe(rid):
    body = request.json or {}
    recipes = load_recipes(RECIPES_FILE)

    for r in recipes:
        if r["id"] == rid:

            if "title" in body:
                r["title"] = body["title"]

            # Update steps while keeping done status
            if "steps" in body and isinstance(body["steps"], list):
                new_steps = []
                for i, s in enumerate(body["steps"]):
                    done = r["steps"][i]["done"] if i < len(r["steps"]) else False
                    new_steps.append({
                        "text": s.get("text", s) if isinstance(s, dict) else str(s),
                        "done": bool(s.get("done", done)) if isinstance(s, dict) else done
                    })
                r["steps"] = new_steps

            # Update image_url
            if "image_url" in body:
                r["image_url"] = body["image_url"]

            # Update ingredients if provided
            if "ingredients" in body:
                r["ingredients"] = body["ingredients"]

            save_recipes(recipes, RECIPES_FILE)
            return jsonify({"ok": True, "recipe": r}), 200

    return jsonify({"ok": False, "error": "Not found"}), 404

@app.route("/api/recipes/<rid>", methods=["DELETE"])
def delete_recipe(rid):
    recipes = load_recipes(RECIPES_FILE)
    new = [r for r in recipes if r["id"] != rid]
    if len(new) == len(recipes):
        return jsonify({"ok": False, "error": "Not found"}), 404
    save_recipes(new, RECIPES_FILE)
    return jsonify({"ok": True}), 200

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"}), 200

# Image upload routes
@app.route("/api/upload", methods=["POST"])
def upload_image():
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"ok": False, "error": "No selected file"}), 400
    if not allowed_file(file.filename):
        return jsonify({"ok": False, "error": "Invalid file type"}), 400
    filename = secure_filename(file.filename)
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    saved_name = f"{timestamp}-{filename}"
    file.save(os.path.join(UPLOAD_FOLDER, saved_name))
    return jsonify({"ok": True, "url": f"/uploads/{saved_name}"}), 200

@app.route("/uploads/<path:filename>")
def serve_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
