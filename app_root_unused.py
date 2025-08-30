# app.py
import os, ssl, smtplib, traceback
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from flask import Flask, jsonify
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

IST = ZoneInfo("Asia/Kolkata")
UTC = ZoneInfo("UTC")

FROM_EMAIL = os.getenv("EMAIL")
APP_PASS = os.getenv("APP_PASS")
TO_EMAIL = "nrveeresh327@gmail.com"  # your inbox


def log(msg):
    print(
        f"[VA BOT] {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')} | {msg}"
    )


if not FROM_EMAIL or not APP_PASS:
    raise SystemExit(
        "❌ EMAIL or APP_PASS missing. Set Replit Secrets and Restart the Repl."
    )


def build_files():
    today = datetime.now(IST).strftime("%d-%m-%Y")
    summary = f"{today} summary report.pdf"  # locked with 'MY OG' by your generator
    invoices = f"{today} invoices.pdf"  # open
    return [(summary, Path(summary).name), (invoices, Path(invoices).name)]


def attach_file(msg, path, filename):
    p = Path(path)
    if not p.exists() or p.stat().st_size < 1024:  # skip missing/empty
        msg.attach(
            MIMEText(f"⚠️ Skipped attachment: {filename} (missing/too small)",
                     "plain"))
        log(f"⚠️ Skipped attachment: {filename}")
        return
    with open(p, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition",
                    f'attachment; filename="{filename}"')
    msg.attach(part)


def send_email_now():
    try:
        html = f"<p>Boss, daily report for {datetime.now(IST).strftime('%d-%m-%Y')} ✅</p>"
        files = build_files()

        msg = MIMEMultipart()
        msg["From"] = FROM_EMAIL
        msg["To"] = TO_EMAIL
        msg["Subject"] = "VA Bot — Daily Report (Auto)"
        msg.attach(MIMEText(html, "html"))
        for p, n in files:
            attach_file(msg, p, n)

        with smtplib.SMTP_SSL("smtp.gmail.com",
                              465,
                              context=ssl.create_default_context()) as s:
            s.login(FROM_EMAIL, APP_PASS)
            s.sendmail(FROM_EMAIL, [TO_EMAIL], msg.as_string())

        log(f"📧 Sent to {TO_EMAIL}")
        return True, "sent"
    except Exception as e:
        log("❌ Send failed:\n" + traceback.format_exc())
        return False, str(e)


# ---- Flask app for UptimeRobot + manual triggers ----
app = Flask(__name__)


@app.get("/")
def home():
    return """
    <h1>VA Bot is running ✅</h1>
    <p>IST scheduler: 10:00 AM daily</p>
    <ul>
      <li><a href="/health">/health</a> — status & time</li>
      <li><a href="/send-now">/send-now</a> — send email instantly</li>
    </ul>
    """


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "ist_now": datetime.now(IST).isoformat(),
        "utc_now": datetime.now(UTC).isoformat()
    })


@app.get("/send-now")
def send_now():
    ok, msg = send_email_now()
    return (jsonify({"ok": ok, "msg": msg}), 200 if ok else 500)


# ---- APScheduler: fire every day at 10:00 IST ----
scheduler = BackgroundScheduler(timezone=IST)
scheduler.add_job(send_email_now, CronTrigger(hour=10,
                                              minute=0))  # 10:00 AM IST
scheduler.start()
log("Scheduler started (daily 10:00 AM IST).")

if __name__ == "__main__":
    # Replit usually sets $PORT; default to 8000 if missing
    port = int(os.getenv("PORT", "8000"))
    log(f"IST now: {datetime.now(IST)} | UTC now: {datetime.now(UTC)}")
    log(f"Serving Flask on port {port}. Health at /health, manual trigger at /send-now"
        )
    app.run(host="0.0.0.0", port=port)
