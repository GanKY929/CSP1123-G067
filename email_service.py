import smtplib
import threading
import config
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

_smtp_connection = None
_smtp_lock = threading.Lock()

def _get_smtp():
    global _smtp_connection
    try:
        if _smtp_connection is None:
            raise Exception("No connection")
        _smtp_connection.noop()
        return _smtp_connection
    except:
        _smtp_connection = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        _smtp_connection.login(config.OFFICIAL_GMAIL, config.GMAIL_APP_PASSWORD)
        return _smtp_connection

def _send(recipient, subject, body_text, body_html=None):
    try:
        if body_html:
            msg = MIMEMultipart("alternative")
            msg.attach(MIMEText(body_text, "plain"))
            msg.attach(MIMEText(body_html, "html"))
        else:
            msg = MIMEText(body_text, "plain")

        msg["Subject"] = subject
        msg["From"] = f"MMU InfoHUB <{config.OFFICIAL_GMAIL}>"
        msg["To"] = recipient

        with _smtp_lock:
            smtp = _get_smtp()
            smtp.sendmail(config.OFFICIAL_GMAIL, recipient, msg.as_string())

        print(f"[EMAIL] Sent to {recipient} | Subject: {subject}")

    except Exception as e:
        print(f"[EMAIL] Failed to send to {recipient}: {e}")

def send_async(recipient, subject, body_text, body_html=None):
    threading.Thread(
        target=_send,
        args=(recipient, subject, body_text, body_html),
        daemon=True
    ).start()

# ─── Pre-built email types ───────────────────────────────

def send_otp(user_email, otp_code):
    subject = "MMUinfo | OTP Verification"
    body_text = f"Your OTP code is: {otp_code}\n\nThis code will expire in 5 minutes.\n\nIf you did not request this, please ignore this email."
    body_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 400px; margin: auto;">
        <h2 style="color: #333;">MMU InfoHUB</h2>
        <p>Your OTP verification code is:</p>
        <h1 style="letter-spacing: 8px; color: #4A90E2;">{otp_code}</h1>
        <p style="color: #888; font-size: 13px;">This code expires in 5 minutes.<br>If you did not request this, ignore this email.</p>
    </div>
    """
    send_async(user_email, subject, body_text, body_html)

def send_feedback(username, user_email, comment, date):
    subject = f"User Feedback | {date}"
    body_text = f"Username: {username}\nEmail: {user_email}\n\n{comment}"
    send_async(config.OFFICIAL_GMAIL, subject, body_text)