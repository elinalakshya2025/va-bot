#!/usr/bin/env python3
"""
DailyReport/send_daily_report.py

Flask microservice to send daily report emails with:
- Encrypted summary PDF (code-lock: 'MY OG' by default)
- Invoices PDF attached
- Approval endpoint for the Boss to approve the day's actions
- Auto-resume after 10 minutes if no approval
- Runner auto-resume endpoint to receive the auto-resume trigger

Usage:
  Export the required env vars (VA_EMAIL, VA_PASSWORD). Optionally set PORT and EXTERNAL_HOST.
  Ensure DailyReport/out/<DD-MM-YYYY>_summary_report.pdf and _invoices.pdf exist before calling /send-report.

Notes:
- Uses PyPDF2 for pure-Python PDF encryption fallback.
- If you prefer qpdf, the code will try to use it first, then fallback to PyPDF2.

"""

import os
import sys
import threading
import time
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, abort
from email.message import EmailMessage
import smtplib
import ssl

# Try optional imports
try:
    import requests
except Exception:
    requests = None

try:
    from PyPDF2 import PdfReader, PdfWriter
except Exception:
    PdfReader = None
    PdfWriter = None

# Configuration
APPROVAL_TIMEOUT = int(os.getenv("APPROVAL_TIMEOUT_S",
                                 "600"))  # default 10 minutes
USER_EMAIL = os.getenv("USER_EMAIL", "nrveeresh327@gamil.com")  # from memory
CODE_LOCK = os.getenv("CODE_LOCK", "MY OG")
VA_EMAIL = os.getenv("VA_EMAIL")
VA_PASSWORD = os.getenv("VA_PASSWORD")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
PORT = int(os.getenv("PORT", "5000"))
EXTERNAL_HOST = os.getenv("EXTERNAL_HOST", f"http://localhost:{PORT}")
OUT_DIR = Path(os.getenv("OUT_DIR", "DailyReport/out"))

if not OUT_DIR.exists():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
LOG = logging.getLogger("send_daily_report")

app = Flask(__name__)

# approval_events keeps track of report states
# report_id -> {"approved": bool, "timer": threading.Timer, "created_at": datetime}
approval_events = {}
approval_lock = threading.Lock()

# ---------------- PDF encryption helpers ----------------


def encrypt_with_qpdf(src_path: Path, dest_path: Path, password: str) -> bool:
    """Try to encrypt PDF using qpdf command line. Returns True on success."""
    try:
        cmd = [
            "qpdf", "--encrypt", password, password, "256", "--",
            str(src_path),
            str(dest_path)
        ]
        LOG.info("Trying qpdf encrypt: %s", " ".join(cmd))
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        LOG.info("qpdf encrypt failed: %s", e)
        return False


def encrypt_with_pypdf2(src_path: Path, dest_path: Path,
                        password: str) -> bool:
    """Encrypt PDF using PyPDF2. Returns True on success or False if PyPDF2 missing or error."""
    if PdfReader is None or PdfWriter is None:
        LOG.info("PyPDF2 not available for PDF encryption.")
        return False
    try:
        reader = PdfReader(str(src_path))
        writer = PdfWriter()
        for p in reader.pages:
            writer.add_page(p)
        writer.encrypt(user_pwd=password, owner_pwd=password, use_128bit=True)
        with open(dest_path, "wb") as fh:
            writer.write(fh)
        return True
    except Exception as e:
        LOG.exception("PyPDF2 encryption failed: %s", e)
        return False


def build_and_encrypt_summary(report_date_str: str):
    """Return tuple (summary_path_to_attach, invoice_path_to_attach)
    summary_path_to_attach will be an encrypted file if encryption succeeded, otherwise original summary.
    """
    summary = OUT_DIR / f"{report_date_str}_summary_report.pdf"
    invoice = OUT_DIR / f"{report_date_str}_invoices.pdf"

    if not summary.exists():
        LOG.warning("Summary PDF missing: %s", summary)
    if not invoice.exists():
        LOG.warning("Invoice PDF missing: %s", invoice)

    enc_summary = OUT_DIR / f"{report_date_str}_summary_report.enc.pdf"

    # Prefer qpdf if present, else fallback to PyPDF2
    if encrypt_with_qpdf(summary, enc_summary, CODE_LOCK):
        LOG.info("Encrypted summary using qpdf: %s", enc_summary)
        return enc_summary, invoice

    if encrypt_with_pypdf2(summary, enc_summary, CODE_LOCK):
        LOG.info("Encrypted summary using PyPDF2: %s", enc_summary)
        return enc_summary, invoice

    LOG.warning("Falling back to sending original summary without encryption.")
    return summary, invoice


# ---------------- Email helpers ----------------


def send_via_smtp(msg: EmailMessage) -> None:
    if VA_EMAIL is None or VA_PASSWORD is None:
        LOG.error("VA_EMAIL or VA_PASSWORD not set. Cannot send email.")
        raise RuntimeError(
            "Missing SMTP credentials. Set VA_EMAIL and VA_PASSWORD environment variables."
        )

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls(context=context)
        s.login(VA_EMAIL, VA_PASSWORD)
        s.send_message(msg)
        LOG.info("Email sent to %s", msg["To"])


def build_approval_email(report_date_str: str, report_id: str) -> EmailMessage:
    enc_summary, invoice = build_and_encrypt_summary(report_date_str)

    approval_link = f"{EXTERNAL_HOST}/approve/{report_id}"
    msg = EmailMessage()
    msg["Subject"] = f"{report_date_str} summary report"
    msg["From"] = VA_EMAIL or "va-bot@example.com"
    msg["To"] = USER_EMAIL

    body = f"""
Boss,

VA Bot executed tasks for {report_date_str}.

Please click APPROVE to allow VA Bot to proceed with today's actions.
APPROVE LINK: {approval_link}

If no approval within {APPROVAL_TIMEOUT // 60} minutes, VA Bot will auto-resume.

Summary PDF is code-locked with passcode: {CODE_LOCK}
"""
    msg.set_content(body)

    # Attach files if present
    for path in (enc_summary, invoice):
        try:
            if path and Path(path).exists():
                with open(path, "rb") as fh:
                    data = fh.read()
                filename = Path(path).name
                msg.add_attachment(data,
                                   maintype="application",
                                   subtype="pdf",
                                   filename=filename)
                LOG.info("Attached file %s", filename)
            else:
                LOG.warning("Attachment missing, not attaching: %s", path)
        except Exception:
            LOG.exception("Failed to attach file: %s", path)

    return msg


# ---------------- Flask endpoints ----------------


@app.route("/send-report", methods=["GET", "POST"])
def send_report():
    report_date_str = datetime.now().strftime("%d-%m-%Y")
    report_id = datetime.now().strftime("%Y%m%d%H%M%S")

    try:
        msg = build_approval_email(report_date_str, report_id)
        send_via_smtp(msg)
    except Exception as e:
        LOG.exception("Failed to send approval email: %s", e)
        return jsonify({"status": "error", "detail": str(e)}), 500

    # start auto-resume timer
    def _auto_resume():
        with approval_lock:
            ev = approval_events.get(report_id)
            if not ev:
                LOG.info("Auto-resume timer fired but event missing for %s",
                         report_id)
                return
            if ev.get("approved"):
                LOG.info("Report %s already approved; skipping auto-resume.",
                         report_id)
                return
            LOG.info("Auto-resume triggered for report %s", report_id)
        # attempt to call runner auto-resume endpoint
        if requests is not None:
            try:
                runner_url = f"{EXTERNAL_HOST}/runner/auto-resume"
                LOG.info("Calling runner auto-resume: %s", runner_url)
                requests.post(runner_url,
                              json={"report_id": report_id},
                              timeout=10)
            except Exception:
                LOG.exception("Failed to notify runner auto-resume endpoint")
        else:
            LOG.warning(
                "Requests library not available; cannot call runner auto-resume endpoint."
            )

    t = threading.Timer(APPROVAL_TIMEOUT, _auto_resume)
    with approval_lock:
        approval_events[report_id] = {
            "approved": False,
            "timer": t,
            "created_at": datetime.now()
        }
    t.start()

    LOG.info("Sent approval email for report %s", report_id)
    return jsonify({
        "status": "sent",
        "report_id": report_id,
        "report_date": report_date_str
    })


@app.route("/approve/<report_id>", methods=["GET"])
def approve(report_id):
    with approval_lock:
        ev = approval_events.get(report_id)
        if not ev:
            LOG.warning("Approve called for invalid report id %s", report_id)
            return "Invalid or expired report id", 404
        if ev.get("approved"):
            LOG.info("Report %s already approved", report_id)
            return "Already approved", 200
        ev["approved"] = True
        timer = ev.get("timer")
        if timer:
            try:
                timer.cancel()
            except Exception:
                pass

    LOG.info("Report %s approved by user", report_id)
    # You can trigger any immediate actions here: e.g., call internal runner endpoint
    # Example: notify runner to proceed
    if requests is not None:
        try:
            runner_url = f"{EXTERNAL_HOST}/runner/approve-callback"
            LOG.info("Notifying runner approve-callback: %s", runner_url)
            requests.post(runner_url,
                          json={"report_id": report_id},
                          timeout=10)
        except Exception:
            LOG.exception("Failed to notify runner approve-callback endpoint")

    return "Approved. VA Bot will proceed.", 200


# Minimal runner endpoints to be used by this service (can be expanded by runner service)
@app.route("/runner/auto-resume", methods=["POST"])
def runner_auto_resume():
    data = request.get_json(silent=True) or {}
    report_id = data.get("report_id")
    LOG.info("Runner auto-resume called for report_id=%s", report_id)
    # Implement runner resume logic here. For now just log.
    return jsonify({
        "status": "runner_auto_resume_received",
        "report_id": report_id
    })


@app.route("/runner/approve-callback", methods=["POST"])
def runner_approve_callback():
    data = request.get_json(silent=True) or {}
    report_id = data.get("report_id")
    LOG.info("Runner approve-callback received for report_id=%s", report_id)
    # Implement post-approval actions here.
    return jsonify({
        "status": "runner_approve_received",
        "report_id": report_id
    })


# Health endpoint
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "time": datetime.now().isoformat()})


if __name__ == "__main__":
    LOG.info("Starting send_daily_report Flask app on port %s", PORT)
    # Provide a helpful startup hint if credentials missing
    if VA_EMAIL is None or VA_PASSWORD is None:
        LOG.warning(
            "VA_EMAIL or VA_PASSWORD env vars are not set. Set them to enable email sending."
        )
    app.run(host="0.0.0.0", port=PORT)
