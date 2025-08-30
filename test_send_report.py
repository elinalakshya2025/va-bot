from main import send_yesterday_report

if __name__ == "__main__":
    print("[TEST] Sending yesterday's report...")
    send_yesterday_report()
    print("[TEST] Done sending yesterday's report.")

# send_report_email.py
import os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

EMAIL = os.getenv("ELINA_EMAIL")  # sender = Elina Gmail
PASSWORD = os.getenv("APP_PASSWORD")  # Gmail App password
RECEIVER = "nrveeresh327@gmail.com"  # Boss's email


def send_report(summary_pdf, invoice_pdf, report_date):
    """
    Sends daily/weekly report email with summary (locked) and invoice attachment.
    summary_pdf: path to summary report (already encrypted with passcode "MY OG")
    invoice_pdf: path to invoice report
    report_date: string like "17-08-2025"
    """

    subject = f"VA Bot Report - {report_date}"
    body = f"""
    Boss,

    Please find attached today's VA Bot reports:

    1. Summary Report (🔒 password protected with 'MY OG')
    2. Invoice Report

    As usual, click the approval button in the email body to continue the schedule.
    """

    # Build email
    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Attach summary (locked)
    with open(summary_pdf, "rb") as f:
        part = MIMEApplication(f.read(), Name=os.path.basename(summary_pdf))
        part[
            "Content-Disposition"] = f'attachment; filename="{os.path.basename(summary_pdf)}"'
        msg.attach(part)

    # Attach invoice
    with open(invoice_pdf, "rb") as f:
        part = MIMEApplication(f.read(), Name=os.path.basename(invoice_pdf))
        part[
            "Content-Disposition"] = f'attachment; filename="{os.path.basename(invoice_pdf)}"'
        msg.attach(part)

    # Send email
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, RECEIVER, msg.as_string())

    print(f"✅ Report email sent to {RECEIVER}")
