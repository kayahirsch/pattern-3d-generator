from flask import Flask, request, jsonify, render_template
from pattern_logic import generate_pattern_svg
import os

app = Flask(__name__)
OUTPUT_DIR = "patterns"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate-pattern", methods=["POST"])
def generate():
    data = request.get_json()
    object_list = data.get("objects", [])
    include_straps = data.get("include_straps", False)

    try:
        svg_content = generate_pattern_svg(object_list, include_straps, return_string=True)
        return jsonify({"svg": svg_content})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
