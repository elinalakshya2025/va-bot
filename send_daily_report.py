from flask import Flask

# -----------------------------
# Flask app for Render
# -----------------------------
app = Flask(__name__)


@app.route("/")
def index():
    return "✅ VA Bot is running 24/7 on Render!", 200


@app.route("/health")
def health():
    return "OK", 200


# -----------------------------
# App Runner (Render requires this to stay alive)
# -----------------------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))  # Render provides PORT
    print(f"🚀 Starting Flask on port {port}")
    app.run(host="0.0.0.0", port=port)
