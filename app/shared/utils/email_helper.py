import smtplib
import asyncio
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core import config

logger = logging.getLogger("app.email_helper")

def _sync_send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Synchronous SMTP sending logic, meant to be run in a separate thread.
    """
    # Check if SMTP details are missing or empty
    if not config.MAIL_USER or not config.MAIL_PASSWORD:
        logger.warning(
            f"SMTP credentials are not configured in your .env file! "
            f"Unable to send real email. Dumping message payload below:\n"
            f"--------------------------------------------------\n"
            f"To: {to_email}\n"
            f"Subject: {subject}\n"
            f"Body:\n{body}\n"
            f"--------------------------------------------------"
        )
        return False

    try:
        # Create standard MIME multipart message
        msg = MIMEMultipart()
        msg["From"] = config.MAIL_FROM or config.MAIL_USER
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "html"))

        # Connect to SMTP server
        # Standard SMTP starttls utilizes SMTP(host, port)
        server = smtplib.SMTP(config.MAIL_HOST, config.MAIL_PORT)
        server.ehlo()
        if not config.MAIL_SECURE:
            # If not using direct SSL, upgrade to TLS
            server.starttls()
            server.ehlo()
        
        server.login(config.MAIL_USER, config.MAIL_PASSWORD)
        server.sendmail(msg["From"], to_email, msg.as_string())
        server.quit()
        logger.info(f"Successfully sent email to {to_email}")
        return True
    except Exception as e:
        logger.error(
            f"Failed to send email to {to_email} via SMTP: {str(e)}. "
            f"Dumping message payload in console fallback:\n"
            f"--------------------------------------------------\n"
            f"To: {to_email}\n"
            f"Subject: {subject}\n"
            f"Body:\n{body}\n"
            f"--------------------------------------------------"
        )
        return False

async def send_otp_email(to_email: str, otp_code: str, otp_type: str) -> bool:
    """
    Sends an OTP verification email to the user asynchronously using a background thread.
    Prevents blocking FastAPI's main async event loop.
    """
    subject = f"Your Verification OTP for {otp_type.replace('_', ' ').title()}"
    
    # Beautiful rich HTML template
    body = f"""
    <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f7f9fc; padding: 20px; color: #333;">
            <div style="max-width: 500px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #e1e8ed;">
                <h2 style="color: #2b6cb0; text-align: center; margin-top: 0;">Verification Code</h2>
                <p>Hello,</p>
                <p>You requested a one-time password (OTP) for <strong>{otp_type.replace('_', ' ')}</strong> in our CRM system.</p>
                <div style="text-align: center; margin: 30px 0;">
                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 4px; color: #2b6cb0; background: #ebf8ff; padding: 12px 24px; border-radius: 8px; border: 1px dashed #bee3f8;">
                        {otp_code}
                    </span>
                </div>
                <p style="font-size: 14px; color: #718096; text-align: center;">This code is valid for <strong>5 minutes</strong>. Please do not share this code with anyone.</p>
                <hr style="border: 0; border-top: 1px solid #edf2f7; margin: 20px 0;">
                <p style="font-size: 12px; color: #a0aec0; text-align: center; margin-bottom: 0;">This is an automated system email, please do not reply.</p>
            </div>
        </body>
    </html>
    """
    # Execute synchronous smtplib in a background thread executor
    return await asyncio.to_thread(_sync_send_email, to_email, subject, body)
