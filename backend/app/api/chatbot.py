import os
import json
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.connection import get_db
from app.db.models import (
    Home, Device, ChatHistory, DeviceDailySummary, HomeDailySummary,
    Report, Prediction, Recommendation, KnowledgeDocument
)
from app.auth_middleware import get_current_user
from energy.service import get_energy_summary
from energy.prediction import predict_usage
from energy.recommendation import generate_recommendations
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/chatbot", tags=["AI Chatbot"])

class ChatMessageSchema(BaseModel):
    home_id: str
    message: str

class ChatResponseSchema(BaseModel):
    response: str
    history: Optional[List[dict]] = None

def get_rag_context(db: Session, home_id: str) -> str:
    """
    Constructs a detailed markdown context document containing all live energy
    stats, device inventory, forecasts, and savings recommendations for the active home.
    """
    home = db.query(Home).filter(Home.id == home_id).first()
    if not home:
        return "Home not found."
        
    devices = db.query(Device).filter(Device.home_id == home_id).all()
    summary = get_energy_summary(home_id)
    
    # 0. Live/Today Stats
    today_energy = summary.get("today", {}).get("energy_kwh", 0.0)
    today_cost = summary.get("today", {}).get("cost", 0.0)
    target_bill = summary.get("target_bill", 0.0)
    monthly_energy = summary.get("monthly", {}).get("energy_kwh", 0.0)
    monthly_cost = summary.get("monthly", {}).get("cost", 0.0)
    
    live_stats_md = (
        f"- **Today's Consumption (Up to now)**: {today_energy} kWh (Estimated Cost: ₹{today_cost})\n"
        f"- **Current Month Consumption (To date)**: {monthly_energy} kWh (Current Cost: ₹{monthly_cost})\n"
        f"- **Target Monthly Budget**: ₹{target_bill}\n"
    )
    
    # 1. Device Inventory
    device_md = "| Device Name | Type | Room | Rated Watts | Current Status |\n|---|---|---|---|---|\n"
    for d in devices:
        device_md += f"| {d.name} | {d.device_type} | {d.room_name} | {d.rated_watts}W | {d.status} |\n"
        
    # 2. Daily Device Summaries (Last 10 days)
    dev_summaries = db.query(DeviceDailySummary).filter(
        DeviceDailySummary.home_id == home_id
    ).order_by(DeviceDailySummary.date.desc()).limit(15).all()
    
    dev_sum_md = "| Date | Device Name | Runtime Hours | Energy (kWh) | Cost (INR) |\n|---|---|---|---|---|\n"
    device_name_map = {d.id: d.name for d in devices}
    for s in dev_summaries:
        name = device_name_map.get(s.device_id, "Unknown Device")
        dev_sum_md += f"| {s.date} | {name} | {s.runtime_hours}h | {s.energy_consumed_kwh} | ₹{s.cost_incurred} |\n"
        
    # 3. Home Daily Summaries (Last 10 days)
    home_summaries = db.query(HomeDailySummary).filter(
        HomeDailySummary.home_id == home_id
    ).order_by(HomeDailySummary.date.desc()).limit(10).all()
    
    home_sum_md = "| Date | Total Energy (kWh) | Total Cost (INR) |\n|---|---|---|---|\n"
    for s in home_summaries:
        home_sum_md += f"| {s.date} | {s.total_energy_kwh} | ₹{s.total_cost} |\n"

    # 4. Predictions & Prediction Accuracies
    preds = db.query(Prediction).filter(
        Prediction.device_id.in_([d.id for d in devices])
    ).order_by(Prediction.date.desc()).limit(15).all()
    
    pred_md = "| Date | Device Name | Tomorrow Pred (h) | 7-Day Pred (h) | 30-Day Pred (h) | Accuracy |\n|---|---|---|---|---|---|\n"
    for p in preds:
        name = device_name_map.get(p.device_id, "Unknown Device")
        accuracy_str = f"{p.prediction_accuracy}%" if p.prediction_accuracy is not None else "N/A"
        pred_md += f"| {p.date} | {name} | {p.tomorrow_predicted_hours}h | {p.seven_day_predicted_hours}h | {p.thirty_day_predicted_hours}h | {accuracy_str} |\n"

    # 5. Recommendations
    recos = db.query(Recommendation).filter(
        Recommendation.home_id == home_id,
        Recommendation.status == "active"
    ).all()
    reco_md = ""
    for r in recos:
        reco_md += f"- [{r.type}] {r.message} (Potential Saving: ₹{r.potential_saving})\n"
    if not reco_md:
        reco_md = "No active recommendations at the moment.\n"
        
    # 6. Generated Reports Summary
    reports = db.query(Report).filter(Report.home_id == home_id).order_by(Report.created_at.desc()).limit(5).all()
    reports_md = ""
    for rep in reports:
        reports_md += f"- {rep.type.capitalize()} Report ({rep.start_date} to {rep.end_date}) -> File path: {rep.file_path or 'Local only'}\n"
    if not reports_md:
        reports_md = "No reports generated yet.\n"
        
    # 7. Knowledge Documents uploaded
    knowledge_docs = db.query(KnowledgeDocument).filter(KnowledgeDocument.home_id == home_id).all()
    knowledge_md = ""
    for doc in knowledge_docs:
        knowledge_md += f"- File: {doc.filename} -> URL: {doc.file_url} (Summary: {doc.content_summary})\n"
    if not knowledge_md:
        knowledge_md = "No external knowledge files uploaded.\n"

    context = (
        f"# ENERGY CONTEXT FOR HOME: {home.name}\n"
        f"- **Location**: {home.location}\n"
        f"- **Electricity Rate**: ₹{home.electricity_rate} per kWh\n"
        f"- **Home Type**: {home.home_type}\n\n"
        f"## Live Stats (Today & Month)\n{live_stats_md}\n"
        f"## Live Device Inventory\n{device_md}\n"
        f"## Recent Device Daily Summaries\n{dev_sum_md}\n"
        f"## Recent Home Daily Summaries\n{home_sum_md}\n"
        f"## AI Energy Forecasts & Prediction Accuracy\n{pred_md}\n"
        f"## Active Recommendations & Opportunities\n{reco_md}\n"
        f"## Historical Reports & Files\n{reports_md}\n"
        f"## Knowledge Assets & Uploaded Guides\n{knowledge_md}\n"
    )
    
    return context

@router.get("/history")
def get_chat_history(home_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_email = current_user["email"]
    # Verify access to home
    home = db.query(Home).filter(Home.id == home_id, Home.user_email == user_email).first()
    if not home:
        raise HTTPException(status_code=403, detail="Access denied")
        
    # Fetch GROQ_API_KEY check
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is missing. Chat assistant is disabled."
        )
        
    history_logs = db.query(ChatHistory).filter(
        ChatHistory.home_id == home_id,
        ChatHistory.user_email == user_email
    ).order_by(ChatHistory.created_at.asc()).all()
    
    return [{"role": h.role, "message": h.message, "time": h.created_at.strftime("%I:%M %p")} for h in history_logs]

@router.post("/query", response_model=ChatResponseSchema)
def query_chatbot(data: ChatMessageSchema, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_email = current_user["email"]
    home_id = data.home_id
    message = data.message
    
    # Verify access to home
    home = db.query(Home).filter(Home.id == home_id, Home.user_email == user_email).first()
    if not home:
        raise HTTPException(status_code=403, detail="Access denied")
        
    # Enforce Groq Exclusively
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is missing. AI Chatbot queries are disabled."
        )
        
    # Retrieve complete RAG context
    context = get_rag_context(db, home_id)
    
    response_text = None
    try:
        from langchain_groq import ChatGroq
        from langchain_core.prompts import ChatPromptTemplate
        
        # Setup LangChain Groq client
        llm = ChatGroq(
            temperature=0.2,
            model_name="llama-3.3-70b-versatile",
            groq_api_key=groq_api_key
        )
        
        tz_ist = timezone(timedelta(hours=5, minutes=30))
        current_time_local = datetime.now(tz_ist)
        current_date_str = current_time_local.strftime("%Y-%m-%d")
        current_weekday = current_time_local.strftime("%A")
        formatted_date_time = f"{current_weekday}, {current_date_str} {current_time_local.strftime('%I:%M %p')}"
        yesterday_date_str = (current_time_local - timedelta(days=1)).strftime("%Y-%m-%d")

        messages = [
            ("system", (
                "You are Vidhyuth Netra, a smart energy assistant inspired by Google Home. "
                "You help users manage electricity consumption, device runtimes, bills, and savings. "
                "Below is the current energy state of the user's home. Use this context to answer the user's question accurately.\n\n"
                f"Today's Date & Time: {formatted_date_time}\n"
                f"Use this date/time to resolve relative timeframes: 'today' is {current_date_str}, 'yesterday' is {yesterday_date_str}, "
                "etc., matching them to dates in the context tables below.\n\n"
                f"Context:\n{context}\n\n"
                "Constraints:\n"
                "1. Always base your responses on the real numbers, device tables, forecasts, and accuracies provided in the context.\n"
                "2. Be concise, direct, and conversational. Use bullet points or lists for readability where appropriate.\n"
                "3. If the user asks about something not in the context, clearly state that you do not have that data."
            ))
        ]
        
        messages.append(("user", "{question}"))
        
        prompt = ChatPromptTemplate.from_messages(messages)
        chain = prompt | llm
        res = chain.invoke({"question": message})
        response_text = res.content
    except Exception as e:
        print(f"Groq RAG Query failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to query AI chatbot: {str(e)}"
        )
        
    # Log to ChatHistory
    chat_log = ChatHistory(
        user_email=user_email,
        home_id=home_id,
        role="user",
        message=message
    )
    db.add(chat_log)
    
    bot_log = ChatHistory(
        user_email=user_email,
        home_id=home_id,
        role="assistant",
        message=response_text
    )
    db.add(bot_log)
    db.commit()
    
    # Retrieve chat history
    history_logs = db.query(ChatHistory).filter(
        ChatHistory.home_id == home_id,
        ChatHistory.user_email == user_email
    ).order_by(ChatHistory.created_at.asc()).all()
    
    history = [{"role": h.role, "message": h.message, "time": h.created_at.strftime("%I:%M %p")} for h in history_logs]
    
    return ChatResponseSchema(
        response=response_text,
        history=history
    )
