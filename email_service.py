import threading
import config
from brevo import Brevo
from brevo.transactional_emails import (
    SendTransacEmailRequestSender,
    SendTransacEmailRequestToItem,
)

client = Brevo(api_key=config.EMAIL_API_KEY)

def _send(recipient, subject, body_text, body_html=None):
    try:
        result = client.transactional_emails.send_transac_email(
            subject=subject,
            text_content=body_text,
            html_content=body_html,
            sender=SendTransacEmailRequestSender(
                name="MMU InfoHUB",
                email=config.OFFICIAL_GMAIL,
            ),
            to=[SendTransacEmailRequestToItem(email=recipient)]
        )
        print(f"[EMAIL] Sent to {recipient} | Subject: {subject} | ID: {result.message_id}")
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
