from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import List
from pydantic import BaseModel

from app.db.connection import get_db
from app.db.models import Notification, Home
from app.auth_middleware import get_current_user
from energy.prediction import predict_usage

router = APIRouter(prefix="/notifications", tags=["Notifications"])

class NotificationResponseSchema(BaseModel):
    id: int
    home_id: str
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("", response_model=List[NotificationResponseSchema])
def get_notifications(home_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Verify home ownership
    home = db.query(Home).filter(Home.id == home_id, Home.user_email == current_user["email"]).first()
    if not home:
        raise HTTPException(status_code=404, detail="Home not found")

    # Dynamic check: Does predicted bill exceed target?
    try:
        pred_res = predict_usage(home_id)
        if "error" not in pred_res:
            monthly_cost = pred_res["monthly"]["cost"]
            target_bill = home.target_monthly_bill
            if monthly_cost > target_bill:
                # Check if we already created a warning for today to prevent duplicates
                today_start = datetime.combine(datetime.now(timezone.utc).date(), datetime.min.time())
                existing_alert = db.query(Notification).filter(
                    Notification.home_id == home_id,
                    Notification.type == "warning",
                    Notification.created_at >= today_start
                ).first()

                if not existing_alert:
                    over_amount = monthly_cost - target_bill
                    alert = Notification(
                        home_id=home_id,
                        title="Electricity Budget Limit Exceeded",
                        message=f"Your predicted electricity bill of ₹{round(monthly_cost, 0)} exceeds your monthly target of ₹{round(target_bill, 0)} by ₹{round(over_amount, 0)}! Reduce appliance runtimes to stay within budget.",
                        type="warning",
                        is_read=False
                    )
                    db.add(alert)
                    db.commit()

                    # Trigger email warning if preference allows
                    try:
                        from app.db.models import User
                        user = db.query(User).filter(User.email == home.user_email).first()
                        if user and user.notification_preferences in ["all", "email"]:
                            from app.service import send_otp_email
                            subject = "⚠️ Vidyuth Nethra Alert: Electricity Budget Limit Exceeded"
                            body_html = f"""
                            <html>
                            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9;">
                                    <h2 style="color: #d9534f; border-bottom: 2px solid #d9534f; padding-bottom: 10px;">Vidyuth Nethra Energy Alert</h2>
                                    <p>Hello <strong>{user.name}</strong>,</p>
                                    <p style="font-size: 16px;">This is a warning alert regarding your energy consumption for <strong>{home.name}</strong>.</p>
                                    <div style="background-color: #fff; border-left: 5px solid #d9534f; padding: 15px; margin: 20px 0; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                                        <p style="margin: 0; font-weight: bold; color: #d9534f;">Budget Exceeded Warning!</p>
                                        <p style="margin: 10px 0 0 0;">{alert.message}</p>
                                    </div>
                                    <p>To reduce energy consumption, you can monitor individual appliance usage and view AI recommendations on your dashboard.</p>
                                    <p style="margin-top: 30px; font-size: 12px; color: #777; border-top: 1px solid #ddd; padding-top: 10px;">
                                        You are receiving this email because your notification preferences are set to receive alerts. You can change these preferences at any time in the Settings page.
                                    </p>
                                </div>
                            </body>
                            </html>
                            """
                            send_otp_email(
                                to_email=user.email,
                                otp=alert.message,
                                subject=subject,
                                body_html=body_html
                            )
                    except Exception as email_err:
                        print(f"Failed to send budget warning email: {email_err}")
    except Exception as check_err:
        print(f"Error checking usage limit for notifications: {check_err}")

    # Return notifications (limit to top 20 latest)
    notifications = db.query(Notification).filter(
        Notification.home_id == home_id
    ).order_by(Notification.created_at.desc()).limit(20).all()
    
    return notifications

@router.post("/{notification_id}/read")
def mark_notification_read(notification_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    notif.is_read = True
    db.commit()
    return {"success": True}
