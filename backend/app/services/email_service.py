"""
MediTraceX Email Notification & OTP Dispatch Service
Supports Gmail SMTP & Custom TLS SMTP Mail Servers.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any
import logging

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def is_configured() -> bool:
        """Returns True if SMTP credentials are provided in configuration."""
        return bool(settings.SMTP_USER and settings.SMTP_PASSWORD)

    @classmethod
    def send_otp_email(cls, to_email: str, user_name: str, otp_code: str) -> Dict[str, Any]:
        """
        Sends a 6-digit password reset OTP email to the user.
        If SMTP is not configured, logs to console and returns status gracefully.
        """
        if not cls.is_configured():
            print(f"\n📧 [EmailService Notice] SMTP not configured in .env.")
            print(f"   Target Email : {to_email}")
            print(f"   Generated OTP: {otp_code}")
            return {
                "sent": False,
                "reason": "SMTP credentials (SMTP_USER / SMTP_PASSWORD) not configured in .env",
                "otp": otp_code
            }

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"Your MediTraceX Password Reset Code: {otp_code}"
            msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_USER}>"
            msg["To"] = to_email

            plain_text = (
                f"Hello {user_name},\n\n"
                f"You recently requested to reset your password for MediTraceX.\n"
                f"Your 6-digit verification code is: {otp_code}\n\n"
                f"This code will expire in 15 minutes.\n"
                f"If you did not request a password reset, please ignore this email.\n\n"
                f"— The MediTraceX Healthcare Team"
            )

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
              <meta charset="utf-8">
              <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 24px; color: #1e293b; }}
                .container {{ max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
                .header {{ background: #134e4a; padding: 24px; text-align: center; color: #ffffff; }}
                .header h1 {{ margin: 0; font-size: 22px; font-weight: 700; letter-spacing: -0.5px; }}
                .header p {{ margin: 4px 0 0; font-size: 13px; color: #99f6e4; }}
                .body {{ padding: 28px 24px; }}
                .otp-box {{ background: #f0fdfa; border: 2px dashed #0d9488; border-radius: 8px; padding: 20px; text-align: center; margin: 24px 0; }}
                .otp-code {{ font-size: 34px; font-weight: 800; letter-spacing: 8px; color: #0f766e; font-family: monospace; }}
                .note {{ font-size: 13px; color: #64748b; line-height: 1.5; }}
                .footer {{ background: #f1f5f9; padding: 16px 24px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0; }}
              </style>
            </head>
            <body>
              <div class="container">
                <div class="header">
                  <h1>MediTraceX</h1>
                  <p>Intelligent Medicine Availability & Pharmacy Discovery</p>
                </div>
                <div class="body">
                  <h2 style="margin-top:0; font-size: 18px; color: #0f172a;">Password Reset Verification</h2>
                  <p>Hello <strong>{user_name}</strong>,</p>
                  <p>We received a request to reset the password for your MediTraceX account. Use the verification code below to proceed:</p>
                  
                  <div class="otp-box">
                    <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 1.5px; color: #0d9488; margin-bottom: 6px; font-weight: 600;">Your One-Time Passcode</div>
                    <div class="otp-code">{otp_code}</div>
                  </div>

                  <p class="note">⏳ <strong>Notice:</strong> This code is valid for <strong>15 minutes</strong>. For your account security, never share this code with anyone.</p>
                  <p class="note" style="margin-top: 12px;">If you didn't request a password reset, you can safely ignore this email.</p>
                </div>
                <div class="footer">
                  &copy; MediTraceX Platform &bull; Find. Verify. Reach.
                </div>
              </div>
            </body>
            </html>
            """

            msg.attach(MIMEText(plain_text, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            # Connect via SSL 465 first (more reliable across Indian ISPs) or fallback to 587
            user_clean = settings.SMTP_USER.strip()
            pw_clean = settings.SMTP_PASSWORD.replace(" ", "").strip()

            server = None
            try:
                server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=12)
                server.login(user_clean, pw_clean)
                server.send_message(msg)
            except Exception as ssl_err:
                # Fallback to port 587 TLS
                try:
                    if server:
                        try: server.close()
                        except: pass
                    server = smtplib.SMTP("smtp.gmail.com", 587, timeout=12)
                    server.starttls()
                    server.login(user_clean, pw_clean)
                    server.send_message(msg)
                except Exception as tls_err:
                    raise Exception(f"SMTP Auth Failed: {ssl_err}")
            finally:
                if server:
                    try:
                        server.quit()
                    except:
                        pass

            print(f" [EmailService] OTP email successfully dispatched to {to_email}!")
            return {"sent": True, "target": to_email}

        except Exception as e:
            print(f" [EmailService Error] Failed to send email to {to_email}: {e}")
            return {
                "sent": False,
                "error": str(e),
                "reason": "SMTP dispatch error. Check credentials or connection."
            }

email_service = EmailService()
