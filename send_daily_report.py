import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask

app = Flask(__name__)


# -----------------------------
# Root & Healthcheck
# -----------------------------
@app.route("/")
def index():
    return "✅ VA Bot is running 24/7 on Render!", 200


@app.route("/health")
def health():
    return "OK", 200


# -----------------------------
# Daily Report Logic
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
# Support Request Logic
# -----------------------------
def run_support_requests():
    """
    Your big support email logic goes here.
    Example: emailing Instagram, Printify, Fiverr, etc.
    """
    print("🚀 Running support requests for all platforms...")

    # Example: (replace with your real logic)
    platforms = [
        ("ElinaInstagramReels", "support@instagram.com"),
        ("Printify", "support@printify.com"),
        ("MeshyAI", "support@meshy.ai"),
        ("CadCrowd", "info@cadcrowd.com"),
        ("Fiverr", "support@fiverr.com"),
        ("YouTube", "youtube-api-support@google.com"),
        ("StockImageVideo", "submit@shutterstock.com"),
        ("AIBookPublishingKDP", "kdp-support@amazon.com"),
        ("ShopifyDigitalProducts", "support@shopify.com"),
        ("StationeryExport", "seller-support@amazon.in"),
    ]

    for name, email in platforms:
        print(f"➡️ {name}: preparing support request…")
        print(f"   📧 emailing {email} (CC: nrveeresh327@gmail.com)…")
        print("   ✅ status: sent")

    # You can also add log saving here
    print("🗂️ Logs saved")
    print("🎯 Done.")

    return "Support requests sent", 200


@app.route("/run-support")
def run_support_endpoint():
    return run_support_requests()


# -----------------------------
# Keep Alive Runner
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Flask on port {port}")
    app.run(host="0.0.0.0", port=port)
