"""
Email Service Module.

Handles the asynchronous sending of emails using fastapi-mail.
"""
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from emova.api.core.config import settings
from pydantic import EmailStr

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER or "",
    MAIL_PASSWORD=settings.SMTP_PASSWORD or "",
    MAIL_FROM=settings.EMAILS_FROM_EMAIL or "no-reply@emova.com",
    MAIL_PORT=settings.SMTP_PORT or 587,
    MAIL_SERVER=settings.SMTP_SERVER or "smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

fast_mail = FastMail(conf)

async def send_recovery_email(email: EmailStr, code: str):
    """
    Sends an email with the password recovery code.
    """
    html = f"""
    <html>
        <body>
            <h2>Password Recovery</h2>
            <p>You have requested to reset your password.</p>
            <p>Your recovery code is: <strong>{code}</strong></p>
            <p>This code will expire in 15 minutes.</p>
            <p>If you did not request this, please ignore this email.</p>
        </body>
    </html>
    """
    
    message = MessageSchema(
        subject="EMOVA - Password Recovery Code",
        recipients=[email],
        body=html,
        subtype=MessageType.html
    )

    await fast_mail.send_message(message)
