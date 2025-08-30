from login_manager import get_login
import os, json, threading
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

import pdfkit
from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path
from alert_guard import is_paused, alert_and_pause
from zoneinfo import ZoneInfo

# ==============================
# CONFIG — Secrets & constants
# ==============================
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Kolkata")  # Always IST
STATE_DIR = Path("state")
STATE_DIR.mkdir(exist_ok=True)

# Sender accounts (READ FROM REPLIT SECRETS)
# Must exist in Secrets panel:
# ELINA_EMAIL, APP_PASSWORD, MY_EMAIL, KAEL_EMAIL, KAEL_PASS, RIVA_EMAIL, RIVA_PASS
SENDER_DEFAULT_EMAIL = os.getenv("ELINA_EMAIL")  # Primary bot sender (Elina)
SENDER_DEFAULT_PASS = os.getenv("APP_PASSWORD")  # 16-char Gmail app password
BOSS_EMAIL = os.getenv("MY_EMAIL")  # You
DHURVAYU_EMAIL = os.getenv(
    "RIVA_EMAIL") or BOSS_EMAIL  # If you set a separate one

# Optional member mailboxes for manual assistance (set in Secrets)
TEAM_ACCOUNTS = {
    "Elina": {
        "email": os.getenv("ELINA_EMAIL"),
        "password": os.getenv("ELINA_PASS") or os.getenv("APP_PASSWORD")
    },
    "Kael": {
        "email": os.getenv("KAEL_EMAIL"),
        "password": os.getenv("KAEL_PASS")
    },
    "Riva": {
        "email": os.getenv("RIVA_EMAIL"),
        "password": os.getenv("RIVA_PASS")
    },
}

# Approval security
APPROVAL_TOKEN = os.getenv("APPROVAL_TOKEN", "allow-continue")
APPROVAL_FILE = Path("approval_state.json")

# PDF toolkit
WKHTMLTOPDF_PATH = "/nix/store/hxiay4lkq4389vxnhnb3d0pbaw6siwkw-wkhtmltopdf/bin/wkhtmltopdf"
PDF_LOCK_CODE = "MY OG"

# Storage
OUT_DIR = Path("out")
OUT_DIR.mkdir(exist_ok=True)

# ==============================
# DATA — Streams & Phases
# ==============================
INCOME_STREAMS = [
    {
        "#": 1,
        "System": "Elina Instagram Reels",
        "Handled": "Elina",
        "Monthly": "₹15K–₹50K"
    },
    {
        "#": 2,
        "System": "Printify POD Store",
        "Handled": "Kael + Elina",
        "Monthly": "₹20K–₹2L+"
    },
    {
        "#": 3,
        "System": "Meshy AI Store",
        "Handled": "Kael",
        "Monthly": "₹10K–₹75K"
    },
    {
        "#": 4,
        "System": "Cad Crowd Auto Work",
        "Handled": "Kael + Riva",
        "Monthly": "₹30K–₹1.5L"
    },
    {
        "#": 5,
        "System": "Affiliate Marketing",
        "Handled": "Kael",
        "Monthly": "₹20K–₹2L"
    },
    {
        "#": 6,
        "System": "Lakshya Global – Flights",
        "Handled": "Kael",
        "Monthly": "₹10K–₹75K"
    },
    {
        "#": 7,
        "System": "Lakshya Global – Airbnb",
        "Handled": "Elina",
        "Monthly": "₹20K–₹1.5L"
    },
    {
        "#": 8,
        "System": "Lakshya Global – Cabs/Zoomcar/Ola",
        "Handled": "Kael",
        "Monthly": "₹5K–₹50K"
    },
    {
        "#": 9,
        "System": "DigiTutor Academic",
        "Handled": "Riva",
        "Monthly": "₹1L–₹4L"
    },
    {
        "#": 10,
        "System": "DigiTutor Music",
        "Handled": "Riva",
        "Monthly": "₹50K–₹2L"
    },
    {
        "#": 11,
        "System": "YouTube AI Channel",
        "Handled": "Kael + Elina",
        "Monthly": "₹30K–₹1.5L"
    },
    {
        "#": 12,
        "System": "Pinterest Affiliate System",
        "Handled": "Kael",
        "Monthly": "₹10K–₹50K"
    },
    {
        "#": 13,
        "System": "Gumroad AI Product Store",
        "Handled": "Kael",
        "Monthly": "₹5K–₹30K"
    },
    {
        "#": 14,
        "System": "Etsy Digital Store",
        "Handled": "Elina",
        "Monthly": "₹20K–₹1L"
    },
    {
        "#": 15,
        "System": "Canva Template Store",
        "Handled": "Riva",
        "Monthly": "₹5K–₹25K"
    },
    {
        "#": 16,
        "System": "Notion Template Sales",
        "Handled": "Kael",
        "Monthly": "₹5K–₹30K"
    },
    {
        "#": 17,
        "System": "Substack AI Newsletter",
        "Handled": "Riva",
        "Monthly": "₹5K–₹40K"
    },
    {
        "#": 18,
        "System": "Online Course Sales",
        "Handled": "Kael",
        "Monthly": "₹10K–₹1L"
    },
    {
        "#": 19,
        "System": "AI Storybook Generator",
        "Handled": "Kael",
        "Monthly": "₹10K–₹40K"
    },
    {
        "#": 20,
        "System": "Medium Blogging (Affiliate)",
        "Handled": "Riva",
        "Monthly": "₹5K–₹30K"
    },
    {
        "#": 21,
        "System": "Fiverr Gig Automation",
        "Handled": "Kael",
        "Monthly": "₹10K–₹1L"
    },
    {
        "#": 22,
        "System": "PLR Product Store",
        "Handled": "Kael",
        "Monthly": "₹10K–₹50K"
    },
    {
        "#": 23,
        "System": "Academic Case Study Engine",
        "Handled": "Riva",
        "Monthly": "₹1L–₹4L"
    },
    {
        "#": 24,
        "System": "AI Case Study Seller",
        "Handled": "Riva",
        "Monthly": "₹30K–₹1L"
    },
    {
        "#": 25,
        "System": "Etsy Printable Empire",
        "Handled": "Elina",
        "Monthly": "₹20K–₹1.5L"
    },
    {
        "#": 26,
        "System": "SurpriseMyDay Mini Gigs",
        "Handled": "Kael + Elina",
        "Monthly": "₹50K–₹2L"
    },
    {
        "#": 27,
        "System": "Mini Event Execution Agency",
        "Handled": "Kael",
        "Monthly": "₹75K–₹2.5L"
    },
    {
        "#": 28,
        "System": "AI PDF Report Generator",
        "Handled": "Kael",
        "Monthly": "₹10K–₹60K"
    },
    {
        "#": 29,
        "System": "Case Study Marketplace",
        "Handled": "Riva",
        "Monthly": "₹1L–₹5L"
    },
    {
        "#": 30,
        "System": "Eco Friendly Global Store",
        "Handled": "Kael + Elina",
        "Monthly": "₹50K–₹2L+"
    },
]

PHASES = [
    {
        "Phase": "Phase 1",
        "Duration": "Aug 2025 – Mar 2026 (8 mo)",
        "Target": "₹2.5L – ₹6L"
    },
    {
        "Phase": "Phase 2",
        "Duration": "Apr 2026 – Dec 2026 (9 mo)",
        "Target": "₹4L – ₹9L"
    },
    {
        "Phase": "Phase 3 (Pre-debt)",
        "Duration": "Jan 2027 – Jun 2027 (6 mo)",
        "Target": "₹10L – ₹15L"
    },
]

# All targets are after tax.


# ==============================
# Utilities
# ==============================
def read_json(path, default):
    p = Path(path)
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2), encoding="utf-8")


def html_escape(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def send_email_smtp(sender_email,
                    sender_pass,
                    to_list,
                    subject,
                    html_body,
                    attachments=None):
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(to_list)
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    for f in attachments or []:
        with open(f, "rb") as fp:
            part = MIMEApplication(fp.read(), Name=os.path.basename(f))
        part[
            "Content-Disposition"] = f'attachment; filename="{os.path.basename(f)}"'
        msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_pass)
        server.sendmail(sender_email, to_list, msg.as_string())


def encrypt_pdf(in_path: Path, out_path: Path, password: str):
    reader = PdfReader(str(in_path))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(password)
    with open(out_path, "wb") as fh:
        writer.write(fh)


def pdf_from_html_string(html: str, out_path: Path):
    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
    pdfkit.from_string(html, str(out_path), configuration=config)


# ==============================
# Report rendering
# ==============================
CSS = """
<style>
body{font-family:Arial,Helvetica,sans-serif;margin:24px;color:#222}
h1{margin:0 0 8px}
h2{margin:24px 0 6px}
small{color:#666}
table{border-collapse:collapse;width:100%;margin:8px 0 16px}
th,td{border:1px solid #ddd;padding:8px;font-size:12px}
th{background:#f5f5f5;text-align:left}
.badge{display:inline-block;padding:2px 8px;border-radius:12px;background:#0d6efd;color:#fff;font-size:11px}
.note{background:#fff7e6;border:1px solid #ffd591;padding:8px;border-radius:8px}
.hr{height:1px;background:#eee;margin:16px 0}
</style>
"""


def render_streams_table():
    head = "<tr><th>#</th><th>System Name</th><th>Handled By</th><th>Monthly Potential</th></tr>"
    rows = []
    for row in INCOME_STREAMS:
        rows.append(
            f"<tr><td>{row['#']}</td><td>{html_escape(row['System'])}</td>"
            f"<td>{html_escape(row['Handled'])}</td><td>{row['Monthly']}</td></tr>"
        )
    return f"<table>{head}{''.join(rows)}</table>"


def render_phases_table():
    head = "<tr><th>Phase</th><th>Duration</th><th>Target (After tax)</th></tr>"
    rows = []
    for ph in PHASES:
        rows.append(
            f"<tr><td>{ph['Phase']}</td><td>{ph['Duration']}</td><td>{ph['Target']}</td></tr>"
        )
    return f"<table>{head}{''.join(rows)}</table>"


def render_daily_qa(answers: dict):
    # 8 questions expected keys
    keys = [
        ("q1", "1) What VA Bot has done yesterday"),
        ("q2", "2) What VA Bot will do today"),
        ("q3", "3) What VA Bot will do tomorrow"),
        ("q4", "4) Today's scheduled tasks"),
        ("q5", "5) Status of yesterday's tasks"),
        ("q6", "6) Areas the team is working on"),
        ("q7", "7) Any issues or progress updates"),
        ("q8", "8) Total earnings so far and distance to target"),
    ]
    rows = ["<tr><th>Question</th><th>Answer</th></tr>"]
    for k, label in keys:
        v = html_escape(answers.get(k, "TBD"))
        rows.append(f"<tr><td>{label}</td><td>{v}</td></tr>")
    return f"<table>{''.join(rows)}</table>"


def build_daily_report_html(date_label: str, answers: dict):
    return f"""
<html><head><meta charset="utf-8">{CSS}</head>
<body>
<h1>Daily Report <span class='badge'>{date_label}</span></h1>
<small>Private: income targets & phase targets are visible only to Boss & Dhurvayu.</small>

<h2>Income Streams & Monthly Projections</h2>
{render_streams_table()}

<h2>Phase Planning</h2>
{render_phases_table()}
<div class='note'>All targets are after tax.</div>

<h2>Daily 8 Questions</h2>
{render_daily_qa(answers)}

<div class='hr'></div>
<p><b>Compliance:</b> VA Bot operates 24/7 worldwide with strict ethical & legal boundaries. No gray/illegal actions are permitted.</p>
<p><b>Support:</b> Dhurvayu monitors internal issues and keeps team motivation aligned with monthly targets.</p>
</body></html>
"""


# ==============================
# Approval workflow (10:00 -> 10:10)
# ==============================
def approval_state_key(date_str):
    return f"approved::{date_str}"


def set_approval(date_str, value: bool):
    st = read_json(APPROVAL_FILE, {})
    st[approval_state_key(date_str)] = value
    write_json(APPROVAL_FILE, st)


def get_approval(date_str) -> bool:
    st = read_json(APPROVAL_FILE, {})
    return bool(st.get(approval_state_key(date_str), False))


def send_approval_email():
    today = datetime.now(TZ).date().isoformat()
    approve_url = f"https://{os.getenv('REPL_SLUG','app')}.{os.getenv('REPL_OWNER','repl.co')}.repl.co/approve?token={APPROVAL_TOKEN}&date={today}"
    subject = f"Approval Needed (by 10:10) – {today}"
    body = f"""
    <h2>Good morning, Boss</h2>
    <p>Please approve today's process. If not approved by <b>10:10 AM IST</b>, VA Bot will auto-resume.</p>
    <p><a href="{approve_url}" style="padding:12px 18px;background:#28a745;color:#fff;text-decoration:none;border-radius:6px;">✅ Approve Today</a></p>
    <p style="color:#666">If the button doesn't work, open this URL:<br>{approve_url}</p>
    """
    send_email_smtp(SENDER_DEFAULT_EMAIL, SENDER_DEFAULT_PASS, [BOSS_EMAIL],
                    subject, body)


def proceed_day_if_needed():
    now = datetime.now(TZ)
    date_str = now.date().isoformat()
    if get_approval(date_str):
        # Already approved; proceed with tasks
        generate_and_send_daily(now)
        return
    # Not approved yet: auto-resume at 10:10
    if now.time() >= (datetime(now.year, now.month, now.day, 10, 10,
                               tzinfo=TZ).time()):
        generate_and_send_daily(now)


def generate_and_send_daily(now_dt):
    date_label = now_dt.strftime("%d-%m-%Y")
    # Read optional inputs for 8 questions (kept private in repo; only Boss/Dhurvayu receive)
    qa = read_json("daily_inputs.json", {})
    html = build_daily_report_html(date_label, qa)

    raw_pdf = OUT_DIR / f"{date_label}_daily_report_raw.pdf"
    locked_pdf = OUT_DIR / f"{date_label}_daily_report_locked.pdf"

    pdf_from_html_string(html, raw_pdf)
    encrypt_pdf(raw_pdf, locked_pdf, PDF_LOCK_CODE)

    subject = f"Daily Report (Locked) – {date_label}"
    body = f"""
    <h3>Daily report attached (password: <code>{PDF_LOCK_CODE}</code>)</h3>
    <p>Targets/streams visible only to Boss & Dhurvayu.</p>
    """
    # Send only to Boss & Dhurvayu
    recipients = [BOSS_EMAIL]
    if DHURVAYU_EMAIL and DHURVAYU_EMAIL != BOSS_EMAIL:
        recipients.append(DHURVAYU_EMAIL)

    send_email_smtp(SENDER_DEFAULT_EMAIL, SENDER_DEFAULT_PASS, recipients,
                    subject, body, [str(locked_pdf)])


# ==============================
# Manual assistance helper
# ==============================
def raise_manual_assistance(stream_name: str, owner: str, issue: str):
    acct = TEAM_ACCOUNTS.get(owner)
    if not acct or not acct.get("email") or not acct.get("password"):
        # fallback to default
        acct = {"email": SENDER_DEFAULT_EMAIL, "password": SENDER_DEFAULT_PASS}
    subject = f"[Manual Assist] {stream_name} – {owner}"
    body = f"""
    <h3>Manual assistance needed</h3>
    <p><b>Stream:</b> {html_escape(stream_name)}<br>
       <b>Owner:</b> {html_escape(owner)}</p>
    <p><b>Issue:</b> {html_escape(issue)}</p>
    """
    send_email_smtp(acct["email"], acct["password"], [BOSS_EMAIL], subject,
                    body)


# ==============================
# Flask app for approval
# ==============================
app = Flask(__name__)
from app_lock import require_pin

app = require_pin(app)


@app.get("/approve")
def approve_today():
    token = request.args.get("token", "")
    date_str = request.args.get("date") or datetime.now(TZ).date().isoformat()
    if token != APPROVAL_TOKEN:
        return jsonify({"ok": False, "error": "invalid token"}), 403
    set_approval(date_str, True)
    return f"✅ Approved for {date_str}. VA Bot will proceed.", 200


@app.get("/")
def health():
    return "VA Bot is running (ethical/legal only).", 200


# ==============================
# Scheduler setup
# ==============================
scheduler = BackgroundScheduler(timezone=str(TZ))

# 10:00 — send approval request
scheduler.add_job(send_approval_email, CronTrigger(hour=10, minute=0))

# 10:10 — auto-resume if not approved
scheduler.add_job(proceed_day_if_needed, CronTrigger(hour=10, minute=10))


# Weekly snapshot (optional): Sunday 00:00
def weekly_summary_job():
    now_dt = datetime.now(TZ)
    date_label = now_dt.strftime("%d-%m-%Y")
    html = f"<html><head>{CSS}</head><body><h1>Weekly Summary {date_label}</h1>{render_phases_table()}{render_streams_table()}</body></html>"
    raw = OUT_DIR / f"{date_label}_weekly_raw.pdf"
    locked = OUT_DIR / f"{date_label}_weekly_locked.pdf"
    pdf_from_html_string(html, raw)
    encrypt_pdf(raw, locked, PDF_LOCK_CODE)
    send_email_smtp(
        SENDER_DEFAULT_EMAIL, SENDER_DEFAULT_PASS, [BOSS_EMAIL],
        f"Weekly Summary (Locked) – {date_label}",
        f"<p>Weekly report attached (password: <code>{PDF_LOCK_CODE}</code>).</p>",
        [str(locked)])


scheduler.add_job(weekly_summary_job,
                  CronTrigger(day_of_week="sun", hour=0, minute=0))


def run():
    # Make sure approval state exists for today (default false)
    set_approval(datetime.now(TZ).date().isoformat(), False)
    scheduler.start()
    # Run Flask (Replit keeps this alive 24/7)
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8081")))


if __name__ == "__main__":
    run()

import threading
import time
import requests

# Replace with your live VA Bot URL
SELF_URL = "https://elinalakshya201.VABOT.repl.co"


def self_ping():
    while True:
        try:
            requests.get(SELF_URL)
            print("Self-ping successful")
        except Exception as e:
            print(f"Self-ping failed: {e}")
        time.sleep(240)  # Ping every 4 minutes


# Run self-ping in a separate thread
threading.Thread(target=self_ping, daemon=True).start()

# main.py
import schedule
import time
import sys
from datetime import datetime, timedelta
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ======================
# Load secrets
# ======================
EMAIL = os.getenv("EMAIL")
APP_PASS = os.getenv("APP_PASS")
TO_EMAIL = "nrveeresh327@gmail.com"  # Boss' email

if not EMAIL or not APP_PASS:
    raise ValueError("❌ Missing EMAIL or APP_PASS in Replit Secrets!")


# ======================
# Report Sender Function
# ======================
def send_daily_report():
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    print(f"📩 Sending daily report at {now}")

    subject = f"Daily Report - {datetime.now().strftime('%d-%m-%Y')}"
    body = f"""
    Hello Boss,

    This is your automated daily report generated at {now}.

    ✅ Summary Report (locked with code 'MY OG') attached
    ✅ Invoices attached

    Regards,  
    VA Bot
    """

    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = TO_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465,
                              context=context) as server:
            server.login(EMAIL, APP_PASS)
            server.sendmail(EMAIL, TO_EMAIL, msg.as_string())
        print("✅ Email sent successfully!")
    except Exception as e:
        print("❌ Error while sending email:", e)


# ======================
# Scheduler
# ======================
def run_scheduler():
    print("🕒 Scheduler started... Waiting for 10:00 AM IST every day")
    schedule.every().day.at("10:00").do(send_daily_report)

    while True:
        schedule.run_pending()
        time.sleep(30)


# ======================
# Entry Point
# ======================
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("🚀 Running test mode...")
        send_daily_report()
    else:
        run_scheduler()

import os
import schedule
import time
import threading
from flask import Flask
from send_daily_report import send_daily_report

app = Flask(__name__)


# ---- Scheduler Job ----
def job():
    print("⏰ Running scheduled job...")
    send_daily_report()


# Schedule daily report at 10:00 AM IST
schedule.every().day.at("10:00").do(job)


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


# ---- Flask route (keep app alive + test trigger) ----
@app.route("/")
def home():
    return "✅ VA Bot is running!"


@app.route("/test")
def test():
    send_daily_report()
    return "📧 Test email sent!"


if __name__ == "__main__":
    # Start scheduler in background
    threading.Thread(target=run_schedule, daemon=True).start()

    # Run Flask on a different port (8081 to avoid conflict)
    port = int(os.environ.get("PORT", 8081))
    app.run(host="0.0.0.0", port=port)

from flask import Flask
import os

app = Flask(__name__)


@app.route("/")
def home():
    return "VA Bot Running ✅"


@app.route("/ping")
def ping():
    return "VA Bot is alive ✅"


if __name__ == "__main__":
    keep_alive()
    port = int(os.environ.get("PORT", 8081))
    app.run(host="0.0.0.0", port=port)

# ---------------- KEEP ALIVE (Replit auto-run) ----------------
import threading, time, requests


def keep_alive_ping():
    """Auto-ping your own Replit URL every 4 minutes to keep it awake"""
    while True:
        try:
            url = "https://vabot.elinalakshya201.repl.co"
            requests.get(url)
            print(f"[AUTO-PING] Sent ping to {url}")
        except Exception as e:
            print(f"[AUTO-PING ERROR] {e}")
        time.sleep(240)  # every 4 minutes


# Start pinging in background
threading.Thread(target=keep_alive_ping, daemon=True).start()

# main.py
from login_manager import get_login

# Example: fetch Elina’s login
elina_email, elina_pass = get_login("elina")
print("Testing login for Elina:", elina_email, elina_pass)

# Fetch Kael’s login
kael_email, kael_pass = get_login("kael")
print("Testing login for Kael:", kael_email, kael_pass)

# Fetch Riva’s login
riva_email, riva_pass = get_login("riva")
print("Testing login for Riva:", riva_email, riva_pass)

# Now you can pass these credentials to the right platform login functions
print("✅ Login details loaded safely for all team members.")


@app.route("/resume")
def manual_resume():
    resume()
    return "▶️ Bot resumed manually!"


# ====== AUTO CATCH-UP & DAILY WATCHDOG (paste-at-bottom) ======
from datetime import datetime, time as dtime
from pathlib import Path
import threading, time

# Use existing TZ if defined; else default to IST
try:
    TZ_LOCAL = TZ  # from your file
except NameError:
    from zoneinfo import ZoneInfo
    TZ_LOCAL = ZoneInfo("Asia/Kolkata")

STATE_DIR = Path("state")
STATE_DIR.mkdir(exist_ok=True)


def _flag_path_for_today():
    return STATE_DIR / f"sent-{datetime.now(TZ_LOCAL).date().isoformat()}.flag"


def has_sent_today():
    return _flag_path_for_today().exists()


def mark_sent_today():
    _flag_path_for_today().write_text("ok", encoding="utf-8")


def _safe_send_now():
    try:
        # uses your existing function
        send_daily_report()
        mark_sent_today()
        print("✅ Catch-up: Daily report sent & marked.")
    except Exception as e:
        # If you have alert_guard.py, this will email+pause on failure
        try:
            from alert_guard import alert_and_pause
            alert_and_pause("Catch-up send failed", f"<pre>{e}</pre>")
        except Exception:
            print("❌ Catch-up failed:", e)


def _catchup_once_on_boot():
    now = datetime.now(TZ_LOCAL)
    if not has_sent_today() and now.time() >= dtime(10, 0):
        print("⏩ Missed 10:00 window; sending now...")
        _safe_send_now()


def _daily_watchdog():
    # prevent double start if code is imported twice
    if getattr(_daily_watchdog, "_started", False):
        return
    _daily_watchdog._started = True

    # one-time catch-up when the app boots
    _catchup_once_on_boot()

    # minute-by-minute guard: if 10:00–10:05 and not sent, send it
    while True:
        try:
            now = datetime.now(TZ_LOCAL)
            if not has_sent_today() and dtime(10, 0) <= now.time() <= dtime(
                    10, 5):
                print("⏰ 10:00 window: sending daily report...")
                _safe_send_now()
        except Exception as e:
            print("Watchdog error:", e)
        time.sleep(60)


# launch watchdog in background without touching your server/scheduler
threading.Thread(target=_daily_watchdog, daemon=True).start()
# ====== END WATCHDOG ======
