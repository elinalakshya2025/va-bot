import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load secrets
EMAIL = os.getenv("EMAIL")  # Elina's Gmail (sender)
APP_PASS = os.getenv("APP_PASS")  # Elina's Gmail App Password

print("DEBUG EMAIL:", EMAIL)
print("DEBUG APP_PASS:", APP_PASS)

if not EMAIL or not APP_PASS:
    raise ValueError(
        "Missing EMAIL or APP_PASS secrets! Please add them in Replit Secrets."
    )

# Setup email
msg = MIMEMultipart()
msg['From'] = EMAIL
msg['To'] = "nrveeresh327@gmail.com"  # ✅ Boss's inbox
msg['Subject'] = "VA Bot Test Email"

body = "Hello Boss, this is a test email from Elina’s Gmail via VA Bot."
msg.attach(MIMEText(body, 'plain'))

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL, APP_PASS)
        server.sendmail(EMAIL, msg['To'], msg.as_string())
    print("✅ Email sent successfully to Boss (nrveeresh327@gmail.com)")
except Exception as e:
    print("❌ Error sending email:", e)
