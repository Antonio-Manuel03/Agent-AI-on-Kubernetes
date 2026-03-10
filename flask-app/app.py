from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

YOUTUBE_VIDEO_ID = "8iqB9MGUpL4"
watching_state = False

@app.get("/")
def index():
    return render_template("index.html", video_id=YOUTUBE_VIDEO_ID)

@app.get("/watching/state")
def get_watching_state():
    return jsonify({"watching": watching_state})

@app.post("/watching/state")
def set_watching_state():
    global watching_state
    data = request.get_json(silent=True) or {}
    watching_state = bool(data.get("watching", False))
    return jsonify({"ok": True, "watching": watching_state})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
