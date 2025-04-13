from flask import Flask, request, send_file, jsonify, render_template
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
    try:
        if request.is_json:
            # JSON API call
            data = request.get_json()
            object_list = data.get("objects", [])
            include_straps = data.get("include_straps", False)
        else:
            # HTML form submission
            object_list = request.form.getlist("objects")
            include_straps = bool(request.form.get("include_straps"))

        # Generate SVG pattern
        output_path = generate_pattern_svg(object_list, include_straps)
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Optional separate download route
@app.route("/download-pattern")
def download():
    return send_file(os.path.join(OUTPUT_DIR, "pattern.svg"), as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
