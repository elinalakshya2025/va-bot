import os, smtplib, ssl, json
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# PDFs
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter

IST = ZoneInfo("Asia/Kolkata")
OUTDIR = Path("DailyReport/out"); OUTDIR.mkdir(parents=True, exist_ok=True)

EMAIL = os.getenv("EMAIL")
APP_PASS = os.getenv("APP_PASS")
TO_EMAIL = "nrveeresh327@gamil.com"  # Boss' address

def today_json_path():
    return OUTDIR / datetime.now(IST).strftime("phase1_%Y-%m-%d.json")

def load_results():
    p = today_json_path()
    data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"results":[]}
    return data

def build_html(results):
    items = "".join([f"<li><b>{r.get('task')}</b>: {r.get('status')} — {r.get('details')} (account: {r.get('account','n/a')}) ({r.get('at')})</li>" for r in results])
    return f"<h2>Phase 1 — {datetime.now(IST).strftime('%Y-%m-%d')}</h2><ul>{items or '<li>No items</li>'}</ul>"

def make_pdf(path, title, lines):
    c = canvas.Canvas(str(path), pagesize=A4)
    w, h = A4; y = h - 72
    c.setFont("Helvetica-Bold", 16); c.drawString(72, y, title); y -= 24
    c.setFont("Helvetica", 12)
    for line in lines:
        for segment in [line[i:i+95] for i in range(0, len(line), 95)]:
            c.drawString(72, y, segment); y -= 18
            if y < 72:
                c.showPage(); y = h - 72; c.setFont("Helvetica", 12)
    c.showPage(); c.save()

def encrypt_pdf(src, dst, password):
    reader = PdfReader(str(src)); writer = PdfWriter()
    for page in reader.pages: writer.add_page(page)
    writer.encrypt(password)
    with open(dst, "wb") as f: writer.write(f)

def attach(msg, path, name):
    part = MIMEBase("application", "pdf")
    with open(path, "rb") as f: part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{name}"')
    msg.attach(part)

def send_email(html, attachments):
    if not EMAIL or not APP_PASS:
        raise RuntimeError("Missing EMAIL or APP_PASS in secrets.")
    msg = MIMEMultipart("alternative")
    msg["From"], msg["To"] = EMAIL, TO_EMAIL
    msg["Subject"] = f"VA Bot — Daily Report — {datetime.now(IST).strftime('%Y-%m-%d')}"
    msg.attach(MIMEText(html, "html"))
    for path, name in attachments: attach(msg, path, name)
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as s:
        s.login(EMAIL, APP_PASS); s.sendmail(EMAIL, [TO_EMAIL], msg.as_string())

def main():
    data = load_results(); html = build_html(data.get("results", []))
    plain_summary = OUTDIR / "summary_tmp.pdf"
    enc_summary = OUTDIR / datetime.now(IST).strftime("%d-%m-%Y summary report.pdf")
    invoices = OUTDIR / datetime.now(IST).strftime("%d-%m-%Y invoices.pdf")
    lines = [f"{r.get('task')}: {r.get('status')} — {r.get('details')} ({r.get('at')})" for r in data.get("results", [])]
    make_pdf(plain_summary, "Daily Summary Report", lines or ["No items today."])
    encrypt_pdf(plain_summary, enc_summary, "MY OG")
    make_pdf(invoices, "Invoices (Phase 1)", ["(Placeholder) Invoices will be attached here."])
    send_email(html, [(enc_summary, enc_summary.name), (invoices, invoices.name)])

if __name__ == "__main__":
    try: import reportlab, pypdf  # noqa
    except Exception:
        import subprocess, sys; subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab", "pypdf"])
    main()
