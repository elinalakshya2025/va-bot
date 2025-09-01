import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask

app = Flask(__name__)


# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def index():
    return "✅ VA Bot is running 24/7 on Render!", 200


@app.route("/health")
def health():
    return "OK", 200


# -----------------------------
# Email Sending
# -----------------------------
def send_email(subject, body):
    EMAIL = os.getenv("EMAIL")
    APP_PASS = os.getenv("APP_PASS")
    TO_EMAIL = "nrveeresh327@gmail.com"

    if not EMAIL or not APP_PASS:
        return "❌ Missing EMAIL or APP_PASS", 500

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = TO_EMAIL
    msg.attach(MIMEText(body, "plain"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465,
                              context=context) as server:
            server.login(EMAIL, APP_PASS)
            server.sendmail(EMAIL, TO_EMAIL, msg.as_string())
        return "✅ Email sent", 200
    except Exception as e:
        return f"❌ Error: {e}", 500


@app.route("/send-report")
def send_report():
    return send_email(
        "✅ VA Bot Daily Report",
        "Boss, VA Bot is running 24/7 and sent this daily report.")


@app.route("/run-support")
def run_support():
    return send_email("📨 Support Task Triggered",
                      "Support logic executed successfully!")


# -----------------------------
# App Runner
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Starting Flask on port {port}")
    app.run(host="0.0.0.0", port=port)

from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return "Hello Boss, Flask is alive on Render!", 200


@app.route("/health")
def health():
    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
