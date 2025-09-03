import os
import smtplib
import ssl
import threading
import time
import pandas as pd
from datetime import datetime
from flask import Flask
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pytz

# Import Phase 1 connectors
from vabot.phase1_connectors import (
    get_printify_shops,
    list_models,
    get_channel_stats,
)

# -----------------------------
# Flask app
# -----------------------------
app = Flask(__name__)


@app.route("/")
def index():
    return "✅ VA Bot is running 24/7 on Render!", 200


@app.route("/health")
def health():
    return "OK", 200


@app.route("/send-report")
def send_report():
    send_daily_report()
    return "Manual report sent ✅", 200


# -----------------------------
# Email Sending Logic
# -----------------------------
def send_daily_report():
    EMAIL = os.getenv("EMAIL")
    APP_PASS = os.getenv("APP_PASS")
    TO_EMAIL = "nrveeresh327@gmail.com"

    if not EMAIL or not APP_PASS:
        print("❌ Missing EMAIL or APP_PASS in environment variables!")
        return

    now = datetime.now(pytz.timezone("Asia/Kolkata"))
    now_str = now.strftime("%d-%m-%Y %I:%M %p IST")

    # Load last log
    log_file = "logs/phase1_log.csv"
    if os.path.exists(log_file):
        log_data = pd.read_csv(log_file).tail(10).to_html(index=False)
    else:
        log_data = "<p>No logs yet.</p>"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"✅ VA Bot Daily Report – {now_str}"
    msg["From"] = EMAIL
    msg["To"] = TO_EMAIL

    text = f"Boss, here’s your daily report at {now_str}."
    html = f"""
    <html>
      <body>
        <h2>✅ VA Bot Daily Report</h2>
        <p>Boss, VA Bot is running 24/7 and executed the workflow.</p>
        <p><b>Latest Logs:</b></p>
        {log_data}
        <p>🚀 Mission 2040 on track.</p>
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
        print(f"✅ Daily report email sent successfully at {now_str}")
    except Exception as e:
        print("❌ Error sending daily report:", e)


# -----------------------------
# Real Workflow Runner (Phase 1)
# -----------------------------
def run_phase1_cycle():
    log_file = "logs/phase1_log.csv"
    os.makedirs("logs", exist_ok=True)

    while True:
        now = datetime.now(pytz.timezone("Asia/Kolkata"))
        now_str = now.strftime("%d-%m-%Y %I:%M %p IST")

        print(f"🚀 Running Phase 1 API checks at {now_str}...")

        results = []
        try:
            results.append({
                "Platform": "Printify",
                "Result": str(get_printify_shops())
            })
        except Exception as e:
            results.append({"Platform": "Printify", "Result": f"Error: {e}"})

        try:
            results.append({
                "Platform": "MeshyAI",
                "Result": str(list_models())
            })
        except Exception as e:
            results.append({"Platform": "MeshyAI", "Result": f"Error: {e}"})

        try:
            results.append({
                "Platform":
                "YouTube",
                "Result":
                str(get_channel_stats("UC_x5XG1OV2P6uZZ5FSM9Ttw"))
            })
        except Exception as e:
            results.append({"Platform": "YouTube", "Result": f"Error: {e}"})

        df = pd.DataFrame(results)
        df["Timestamp"] = now_str

        if os.path.exists(log_file):
            df.to_csv(log_file, mode="a", header=False, index=False)
        else:
            df.to_csv(log_file, index=False)

        print(f"✅ Logged results to {log_file}")
        print("⏳ Sleeping for 1 hour...")
        time.sleep(3600)  # 1 hour


# -----------------------------
# App Runner
# -----------------------------
if __name__ == "__main__":
    # Start background workflow thread
    threading.Thread(target=run_phase1_cycle, daemon=True).start()

    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Starting Flask on port {port}")
    app.run(host="0.0.0.0", port=port)
