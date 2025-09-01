from flask import Flask

# -----------------------------
# Minimal Flask app for Render
# -----------------------------
app = Flask(__name__)


@app.route("/")
def index():
    return "✅ VA Bot is running 24/7 on Render!", 200


@app.route("/health")
def health():
    return "OK", 200


# -----------------------------
# App Runner
# -----------------------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT",
                              10000))  # Render provides PORT dynamically
    print(f"🚀 Starting Flask on port {port}")
    app.run(host="0.0.0.0", port=port)

from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return "✅ VA Bot is running on Render!", 200


@app.route("/health")
def health():
    return "OK", 200
# force rebuild
