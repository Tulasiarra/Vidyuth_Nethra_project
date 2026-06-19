import os
import httpx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load .env from project root (two levels above backend/app/)
_env_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),  # backend/app/
    "..",                                          # backend/
    "..",                                          # project root
    ".env"
)
load_dotenv(dotenv_path=os.path.normpath(_env_path), override=True)

from app.db.connection import SessionLocal
from app.db.models import User

def send_otp_email(to_email: str, otp: str, subject: str, body_html: str):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM", smtp_user)

    # Debug: confirm env vars are loaded
    print(f"[EMAIL DEBUG] SMTP_HOST={smtp_host}, SMTP_PORT={smtp_port}, SMTP_USER={smtp_user}, SMTP_FROM={smtp_from}")

    if not all([smtp_host, smtp_port, smtp_user, smtp_pass]):
        print(f"[EMAIL SIMULATION] SMTP credentials not fully set. To: {to_email} | Subject: {subject} | Body: {otp}")
        return False

    try:
        msg = MIMEMultipart("alternative", charset="utf-8")
        msg['From'] = smtp_from
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body_html, 'html', 'utf-8'))

        with smtplib.SMTP(smtp_host, int(smtp_port), timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_from, to_email, msg.as_string())

        print(f"[EMAIL SENT] Successfully sent email to {to_email}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"[EMAIL ERROR] SMTP Authentication failed — check SMTP_USER and SMTP_PASSWORD (use Gmail App Password, not account password): {e}")
        return False
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email via SMTP to {to_email}: {e}")
        return False

# .env already loaded at module import time (see top of file)

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL", "https://ngfkgavqefymfgfvgsps.supabase.co")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY")

def register_user(data):
    try:
        # 1. Sign up on Supabase Auth
        url = f"{SUPABASE_URL}/auth/v1/signup"
        headers = {
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json"
        }
        body = {
            "email": data.email,
            "password": data.password,
            "options": {
                "data": {
                    "full_name": data.name
                }
            }
        }
        
        response = httpx.post(url, headers=headers, json=body)
        
        if response.status_code != 200:
            err_msg = response.json().get("msg", "Registration failed")
            if response.status_code == 429 or "rate limit" in err_msg.lower() or "security" in err_msg.lower() or len(data.email) > 25:
                # Fallback to local DB registration
                db = SessionLocal()
                try:
                    existing = db.query(User).filter(User.email == data.email).first()
                    if not existing:
                        from app.password_utils import hash_password
                        new_user = User(
                            name=data.name,
                            email=data.email,
                            phone_number=None,
                            password_hash=hash_password(data.password),
                            notification_preferences="all",
                            is_verified=False
                        )
                        db.add(new_user)
                        db.commit()

                    # Send confirmation/welcome email for local registration
                    try:
                        from app.jwt_handler import create_access_token
                        confirm_token = create_access_token({"email": data.email, "purpose": "email_verification"})
                        confirm_url = f"http://localhost:5173/#access_token={confirm_token}&type=signup"
                        
                        subject = "📧 Confirm Your Vidyuth Nethra Registration"
                        body_html = f"""
                        <html>
                        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin:0; padding:0; background:#f0f4f8;">
                            <div style="max-width: 600px; margin: 40px auto; padding: 32px; border-radius: 12px; background-color: #ffffff; box-shadow: 0 4px 16px rgba(0,0,0,0.08);">
                                <div style="text-align:center; margin-bottom:24px;">
                                    <span style="font-size:40px;">⚡</span>
                                    <h1 style="color:#00b4d8; margin:8px 0 0; font-size:22px; letter-spacing:1px;">VIDYUTH NETHRA</h1>
                                    <p style="color:#888; font-size:13px; margin:4px 0 0;">AI Smart Home Energy Optimization</p>
                                </div>
                                <hr style="border:none; border-top:1px solid #e2e8f0; margin:20px 0;">
                                <h2 style="color:#1e293b; font-size:20px; margin-bottom:8px;">Confirm your registration, {data.name}! 🎉</h2>
                                <p style="color:#475569;">Thank you for registering with Vidyuth Nethra. Please click the button below to confirm your registration and verify your email address:</p>
                                <div style="text-align:center; margin:28px 0;">
                                    <a href="{confirm_url}" style="background:#00b4d8; color:white; padding:12px 32px; text-decoration:none; border-radius:8px; font-weight:bold; font-size:15px; display:inline-block;">Confirm My Account →</a>
                                </div>
                                <p style="color:#64748b; font-size:13px;">Or copy and paste this link in your browser:</p>
                                <p style="background:#f1f5f9; padding:10px 14px; border-radius:6px; word-break:break-all; font-size:12px; color:#0369a1;">{confirm_url}</p>
                                <p style="margin-top:32px; font-size:11px; color:#94a3b8; border-top:1px solid #e2e8f0; padding-top:16px;">
                                    If you did not create this account, please ignore this email.
                                </p>
                            </div>
                        </body>
                        </html>
                        """
                        send_otp_email(
                            to_email=data.email,
                            otp=f"Confirm registration: {confirm_url}",
                            subject=subject,
                            body_html=body_html
                        )
                    except Exception as e_err:
                        print(f"Failed to send confirmation email for local signup: {e_err}")

                    return {"success": True, "message": "Verification link sent! Please check your email inbox to confirm your account."}
                except Exception as local_err:
                    print(f"Failed to sync user locally on rate-limit fallback: {local_err}")
                finally:
                    db.close()
            return {"success": False, "message": err_msg}
            
        # 2. Sync to local database
        db = SessionLocal()
        try:
            existing = db.query(User).filter(User.email == data.email).first()
            if not existing:
                new_user = User(
                    name=data.name,
                    email=data.email,
                    phone_number=None,
                    password_hash="", # Password is managed by Supabase, local hash empty for safety
                    notification_preferences="all"
                )
                db.add(new_user)
                db.commit()
        except Exception as local_err:
            print(f"Failed to sync user to local DB: {local_err}")
        finally:
            db.close()
            
        return {"success": True, "message": "Verification link sent! Please check your email inbox to confirm your account."}
    except Exception as e:
        return {"success": False, "message": f"Server error: {str(e)}"}


def login_user(data):
    try:
        # Sign in on Supabase Auth
        url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
        headers = {
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json"
        }
        body = {
            "email": data.email,
            "password": data.password
        }
        
        response = httpx.post(url, headers=headers, json=body)
        
        if response.status_code != 200:
            err_msg = response.json().get("error_description", "Invalid login credentials")
            if response.status_code == 429 or "rate limit" in err_msg.lower() or "security" in err_msg.lower() or len(data.email) > 25:
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.email == data.email).first()
                    if user:
                        password_correct = True
                        if user.password_hash:
                            from app.password_utils import verify_password
                            password_correct = verify_password(data.password, user.password_hash)
                        
                        if password_correct:
                            if hasattr(user, "is_verified") and user.is_verified is False:
                                return {"success": False, "message": "Please verify your email address before logging in."}
                            from app.jwt_handler import create_access_token
                            token = create_access_token({"email": data.email})
                            return {"success": True, "token": token}
                        else:
                            return {"success": False, "message": "Wrong password (local verification)"}
                    else:
                        return {"success": False, "message": "User not found locally"}
                except Exception as local_err:
                    print(f"Failed local login fallback: {local_err}")
                finally:
                    db.close()
            return {"success": False, "message": err_msg}
            
        res_data = response.json()
        token = res_data.get("access_token")
        
        # Store user info locally if not exists
        db = SessionLocal()
        try:
            existing = db.query(User).filter(User.email == data.email).first()
            if not existing:
                # Retrieve user name from user object
                user_info = res_data.get("user", {})
                user_metadata = user_info.get("user_metadata", {})
                name = user_metadata.get("full_name", data.email.split("@")[0].capitalize())
                
                new_user = User(
                    name=name,
                    email=data.email,
                    phone_number=None,
                    password_hash="",
                    notification_preferences="all"
                )
                db.add(new_user)
                db.commit()
        except Exception as local_err:
            print(f"Failed to sync user on login: {local_err}")
        finally:
            db.close()
            
        return {"success": True, "token": token}
    except Exception as e:
        return {"success": False, "message": f"Server error: {str(e)}"}
def forgot_password_flow(email: str):
    try:
        # Call Supabase recover endpoint to send email reset link
        url = f"{SUPABASE_URL}/auth/v1/recover"
        headers = {
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json"
        }
        body = {
            "email": email
        }
        response = httpx.post(url, headers=headers, json=body)
        
        if response.status_code != 200:
            err_msg = response.json().get("msg", "Failed to send reset link")
            # Fallback: generate local JWT reset token and email it
            try:
                from app.jwt_handler import create_access_token
                reset_token = create_access_token({"email": email, "purpose": "password_reset"})
                reset_url = f"http://localhost:5173/#access_token={reset_token}&type=recovery"
                subject = "🔐 Vidyuth Nethra — Password Reset Link"
                body_html = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin:0; padding:0; background:#f0f4f8;">
                    <div style="max-width: 600px; margin: 40px auto; padding: 32px; border-radius: 12px; background:#ffffff; box-shadow:0 4px 16px rgba(0,0,0,0.08);">
                        <div style="text-align:center; margin-bottom:24px;">
                            <span style="font-size:40px;">⚡</span>
                            <h1 style="color:#00b4d8; margin:8px 0 0; font-size:22px; letter-spacing:1px;">VIDYUTH NETHRA</h1>
                        </div>
                        <hr style="border:none; border-top:1px solid #e2e8f0; margin:20px 0;">
                        <h2 style="color:#1e293b;">Password Reset Request 🔒</h2>
                        <p style="color:#475569;">We received a request to reset the password for <strong>{email}</strong>. Click the button below to set a new password:</p>
                        <div style="text-align:center; margin:28px 0;">
                            <a href="{reset_url}" style="background:#00b4d8; color:white; padding:14px 36px; text-decoration:none; border-radius:8px; font-weight:bold; font-size:15px; display:inline-block;">Reset My Password →</a>
                        </div>
                        <p style="color:#64748b; font-size:13px;">Or copy and paste this link in your browser:</p>
                        <p style="background:#f1f5f9; padding:10px 14px; border-radius:6px; word-break:break-all; font-size:12px; color:#0369a1;">{reset_url}</p>
                        <p style="color:#94a3b8; font-size:12px;">This link expires in 24 hours. If you did not request a password reset, please ignore this email.</p>
                    </div>
                </body>
                </html>
                """
                send_otp_email(
                    to_email=email,
                    otp=f"Reset Link: {reset_url}",
                    subject=subject,
                    body_html=body_html
                )
                return {"success": True, "message": "Password reset link sent to your email. Please check your inbox."}
            except Exception as e_err:
                print(f"Failed to send local password reset email: {e_err}")
                return {"success": False, "message": err_msg}
            
        return {"success": True, "message": "Password reset link sent to your email. Please check your inbox."}
    except Exception as e:
        return {"success": False, "message": f"Server error: {str(e)}"}

def reset_password_direct_flow(token: str, new_password: str):
    db = SessionLocal()
    try:
        # Try Supabase first (for users registered via Supabase)
        url = f"{SUPABASE_URL}/auth/v1/user"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        body = {"password": new_password}
        response = httpx.put(url, headers=headers, json=body)
        
        if response.status_code == 200:
            user_data = response.json()
            email = user_data.get("email")
            if email:
                from app.password_utils import hash_password
                hashed = hash_password(new_password)
                user = db.query(User).filter(User.email == email).first()
                if user:
                    user.password_hash = hashed
                try:
                    from sqlalchemy import text
                    db.execute(
                        text("UPDATE auth.users SET encrypted_password = :hashed WHERE email = :email"),
                        {"hashed": hashed, "email": email}
                    )
                except Exception:
                    pass  # Ignore if auth schema not accessible
                db.commit()
            return {"success": True, "message": "Password reset successful"}
        
        # Supabase rejected token — try local JWT (for locally registered users)
        try:
            from app.jwt_handler import verify_token
            from app.password_utils import hash_password
            payload = verify_token(token)
            email = payload.get("email")
            purpose = payload.get("purpose")
            if not email or purpose != "password_reset":
                return {"success": False, "message": "Invalid or expired reset token"}
            
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return {"success": False, "message": "User not found"}
            
            user.password_hash = hash_password(new_password)
            db.commit()
            print(f"[RESET] Local password reset successful for {email}")
            return {"success": True, "message": "Password reset successful"}
        except Exception as jwt_err:
            print(f"[RESET] Local JWT verification failed: {jwt_err}")
            return {"success": False, "message": "Invalid or expired reset token. Please request a new reset link."}
            
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Server error: {str(e)}"}
    finally:
        db.close()

def verify_email_flow(token: str):
    db = SessionLocal()
    try:
        from app.jwt_handler import verify_token
        payload = verify_token(token)
        email = payload.get("email")
        purpose = payload.get("purpose")
        
        if not email or purpose != "email_verification":
            return {"success": False, "message": "Invalid or expired verification token."}
            
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return {"success": False, "message": "User not found."}
            
        user.is_verified = True
        db.commit()
        print(f"[VERIFY] Email verification successful for {email}")
        return {"success": True, "message": "Email verified successfully!"}
    except Exception as e:
        db.rollback()
        print(f"[VERIFY] Email verification failed: {str(e)}")
        return {"success": False, "message": f"Verification failed: {str(e)}"}
    finally:
        db.close()