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
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f9; margin: 0; padding: 40px 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
            <div style="background-color: #2F3542; padding: 25px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 26px; letter-spacing: 2px;">EMOVA</h1>
            </div>
            <div style="padding: 40px 30px; color: #333333;">
                <h2 style="margin-top: 0; color: #2F3542; font-size: 22px;">Recuperación de Contraseña</h2>
                <p style="font-size: 16px; line-height: 1.6;">Hola,</p>
                <p style="font-size: 16px; line-height: 1.6;">Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en el sistema <strong>EMOVA</strong>.</p>
                <p style="font-size: 16px; line-height: 1.6;">Por favor, ingresa el siguiente código de verificación en la aplicación:</p>
                
                <div style="text-align: center; margin: 40px 0;">
                    <span style="font-size: 34px; font-weight: bold; background-color: #f4f4f9; border: 1px solid #e0e0e0; padding: 15px 30px; border-radius: 8px; letter-spacing: 6px; color: #2F3542;">
                        {code}
                    </span>
                </div>
                
                <p style="font-size: 14px; color: #666666; margin-top: 10px;">⚠️ Este código expirará en <strong>15 minutos</strong>.</p>
                <p style="font-size: 14px; color: #666666;">Si tú no solicitaste este cambio, simplemente ignora este correo. Tu cuenta seguirá estando segura.</p>
            </div>
            <div style="background-color: #f4f4f9; padding: 20px; text-align: center; font-size: 12px; color: #888888; border-top: 1px solid #eeeeee;">
                &copy; 2026 Sistema EMOVA. Todos los derechos reservados.
            </div>
        </div>
    </body>
    </html>
    """
    
    message = MessageSchema(
        subject="EMOVA - Código de Recuperación de Contraseña",
        recipients=[email],
        body=html,
        subtype=MessageType.html
    )

    await fast_mail.send_message(message)
