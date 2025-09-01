import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
# Email Sending Logic
# -----------------------------
def send_daily_report():
    EMAIL = os.getenv("EMAIL")  # Sender Gmail
    APP_PASS = os.getenv("APP_PASS")  # Gmail App Password
    TO_EMAIL = "nrveeresh327@gmail.com"  # Boss' email

    if not EMAIL or not APP_PASS:
        print("❌ Missing EMAIL or APP_PASS in environment variables!")
        return "Email credentials missing", 500

    # Build email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "✅ VA Bot Daily Report"
    msg["From"] = EMAIL
    msg["To"] = TO_EMAIL

    text = "Boss, VA Bot is running 24/7 and sent this daily report."
    html = """
    <html>
      <body>
        <h2>✅ VA Bot Daily Report</h2>
        <p>Boss,</p>
        <p>VA Bot is running 24/7 on Render and sending updates automatically 🚀</p>
        <p>- Dhruvayu</p>
      </body>
    </html>
    """

    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465,
                              context=context) as server:
            server.login(EMAIL, APP_PASS)
            server.sendmail(EMAIL, TO_EMAIL, msg.as_string())
        print("✅ Daily report email sent successfully to Boss!")
    except Exception as e:
        print("❌ Error sending daily report:", e)
        return f"Error sending email: {e}", 500

    return "Daily report sent", 200


@app.route("/send-report")
def send_report_endpoint():
    return send_daily_report()


# -----------------------------
# App Runner (Render requires this to stay alive)
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render gives dynamic PORT
    print(f"🚀 Starting Flask on port {port}")
    app.run(host="0.0.0.0", port=port)
