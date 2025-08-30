import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email_elina():
    # Load secrets from Replit
    sender_email = os.getenv("ELINA_EMAIL_ADDRESS")
    sender_password = os.getenv("ELINA_EMAIL_PASSWORD")
    receiver_email = os.getenv("TO_EMAIL")

    # Email content
    subject = "Test Email - VA Bot Elina"
    body = """
    <h2>VA Bot - Elina Gmail Test</h2>
    <p>This is a test email sent using Elina's Gmail account.</p>
    """

    # Build email
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        # Gmail SMTP
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("✅ Email sent successfully from Elina's Gmail!")
    except Exception as e:
        print("❌ Failed to send email:", str(e))


if __name__ == "__main__":
    send_email_elina()
