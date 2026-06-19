import json
import io
import csv
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.connection import get_db
from app.db.models import Home, Device, DeviceDailySummary, HomeDailySummary, Recommendation, Report, Prediction
from app.auth_middleware import get_current_user
from app.services.storage import upload_file_to_supabase
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/reports", tags=["Reports"])

class ReportRequestSchema(BaseModel):
    home_id: str
    type: str # "daily", "weekly", "monthly"
    date_str: Optional[str] = None # "YYYY-MM-DD"

def generate_csv_bytes(content: dict) -> bytes:
    device_breakdown = content.get("device_breakdown", [])
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["Vidhyuth Netra Energy Report"])
    writer.writerow(["Home", content.get("home_name")])
    writer.writerow(["Report Type", content.get("type").upper()])
    writer.writerow(["Period", f"{content.get('start_date')} to {content.get('end_date')}"])
    writer.writerow(["Total Consumption (kWh)", content.get("total_energy_kwh")])
    writer.writerow(["Total Cost (INR)", content.get("total_cost")])
    writer.writerow([])
    
    writer.writerow(["Device ID", "Device Name", "Category", "Room", "Runtime (Hours)", "Consumption (kWh)", "Cost (INR)"])
    for d in device_breakdown:
        writer.writerow([
            d.get("device_id"),
            d.get("name"),
            d.get("type"),
            d.get("room"),
            d.get("runtime_hours"),
            d.get("energy_kwh"),
            d.get("cost")
        ])
    return output.getvalue().encode("utf-8")

def generate_pdf_bytes(content: dict) -> bytes:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []
        
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=24,
            textColor=colors.HexColor('#0d9488'),
            spaceAfter=12
        )
        
        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=6
        )
        
        h2_style = ParagraphStyle(
            'H2Style',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.HexColor('#0f172a'),
            spaceBefore=12,
            spaceAfter=8
        )
        
        story.append(Paragraph("VIDHYUTH NETRA ENERGY REPORT", title_style))
        story.append(Paragraph(f"<b>Home:</b> {content.get('home_name')}", body_style))
        story.append(Paragraph(f"<b>Type:</b> {content.get('type').upper()}", body_style))
        story.append(Paragraph(f"<b>Period:</b> {content.get('start_date')} to {content.get('end_date')}", body_style))
        story.append(Paragraph(f"<b>Total Consumption:</b> {content.get('total_energy_kwh')} kWh", body_style))
        story.append(Paragraph(f"<b>Total Electricity Cost:</b> INR {content.get('total_cost')}", body_style))
        story.append(Spacer(1, 16))
        
        story.append(Paragraph("Device Breakdown", h2_style))
        
        data = [["Device Name", "Category", "Room", "Runtime", "Energy", "Cost"]]
        for d in content.get("device_breakdown", []):
            data.append([
                d.get("name"),
                d.get("type"),
                d.get("room"),
                f"{d.get('runtime_hours')}h",
                f"{d.get('energy_kwh')} kWh",
                f"INR {d.get('cost')}"
            ])
            
        t = Table(data, colWidths=[120, 100, 100, 70, 70, 80])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f8fafc'), colors.HexColor('#ffffff')]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
        ]))
        story.append(t)
        
        if content.get("recommendations"):
            story.append(Spacer(1, 16))
            story.append(Paragraph("AI Recommendations", h2_style))
            for r in content["recommendations"]:
                story.append(Paragraph(f"• {r}", body_style))
                
        doc.build(story)
        return pdf_buffer.getvalue()
    except Exception as e:
        # Text-based fallback bytes
        output = io.BytesIO()
        output.write(f"VIDHYUTH NETRA ENERGY REPORT\n".encode())
        output.write(f"=============================\n".encode())
        output.write(f"Home: {content.get('home_name')}\n".encode())
        output.write(f"Type: {content.get('type').upper()}\n".encode())
        output.write(f"Period: {content.get('start_date')} to {content.get('end_date')}\n".encode())
        output.write(f"Total Consumption: {content.get('total_energy_kwh')} kWh\n".encode())
        output.write(f"Total Cost: INR {content.get('total_cost')}\n\n".encode())
        
        output.write(f"Device Breakdown:\n".encode())
        for d in content.get("device_breakdown", []):
            output.write(f"- {d.get('name')} ({d.get('type')} in {d.get('room')}): {d.get('runtime_hours')}h, {d.get('energy_kwh')} kWh, INR {d.get('cost')}\n".encode())
        return output.getvalue()

@router.post("/generate")
def generate_report(data: ReportRequestSchema, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_email = current_user["email"]
    home = db.query(Home).filter(Home.id == data.home_id, Home.user_email == user_email).first()
    if not home:
        raise HTTPException(status_code=403, detail="Access denied")
        
    date_str = data.date_str or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ref_date = datetime.strptime(date_str, "%Y-%m-%d")
    
    if data.type == "daily":
        start_date = date_str
        end_date = date_str
    elif data.type == "weekly":
        start_date = (ref_date - timedelta(days=6)).strftime("%Y-%m-%d")
        end_date = date_str
    elif data.type == "monthly":
        start_date = ref_date.replace(day=1).strftime("%Y-%m-%d")
        import calendar
        last_day = calendar.monthrange(ref_date.year, ref_date.month)[1]
        end_date = ref_date.replace(day=last_day).strftime("%Y-%m-%d")
    else:
        raise HTTPException(status_code=400, detail="Invalid report type")

    summaries = db.query(
        DeviceDailySummary.device_id,
        func.sum(DeviceDailySummary.runtime_hours).label("runtime"),
        func.sum(DeviceDailySummary.energy_consumed_kwh).label("energy"),
        func.sum(DeviceDailySummary.cost_incurred).label("cost")
    ).filter(
        DeviceDailySummary.home_id == data.home_id,
        DeviceDailySummary.date >= start_date,
        DeviceDailySummary.date <= end_date
    ).group_by(DeviceDailySummary.device_id).all()
    
    if not summaries:
        raise HTTPException(
            status_code=400, 
            detail=f"No consumption data available for {ref_date.strftime('%B %Y')}."
        )
    
    devices = db.query(Device).filter(Device.home_id == data.home_id).all()
    device_name_map = {d.id: (d.name, d.device_type, d.room_name) for d in devices}
    
    device_data = []
    total_energy = 0.0
    total_cost = 0.0
    top_device = None
    
    for s in summaries:
        name, d_type, room = device_name_map.get(s.device_id, ("Unknown", "Unknown", "Unknown"))
        cost = float(s.cost or 0.0)
        energy = float(s.energy or 0.0)
        runtime = float(s.runtime or 0.0)
        
        total_energy += energy
        total_cost += cost
        
        device_data.append({
            "device_id": s.device_id,
            "name": name,
            "type": d_type,
            "room": room,
            "runtime_hours": round(runtime, 2),
            "energy_kwh": round(energy, 2),
            "cost": round(cost, 2)
        })
        
    device_data.sort(key=lambda x: x["cost"], reverse=True)
    if device_data:
        top_device = device_data[0]
        
    trend_data = db.query(
        HomeDailySummary.date,
        HomeDailySummary.total_energy_kwh,
        HomeDailySummary.total_cost
    ).filter(
        HomeDailySummary.home_id == data.home_id,
        HomeDailySummary.date >= start_date,
        HomeDailySummary.date <= end_date
    ).order_by(HomeDailySummary.date.asc()).all()
    
    trend = [{"date": t.date, "energy_kwh": round(t.total_energy_kwh, 2), "cost": round(t.total_cost, 2)} for t in trend_data]
    
    recos = db.query(Recommendation).filter(
        Recommendation.home_id == data.home_id,
        Recommendation.status == "active"
    ).all()
    reco_list = [r.message for r in recos]
    
    report_content = {
        "home_name": home.name,
        "type": data.type,
        "start_date": start_date,
        "end_date": end_date,
        "total_energy_kwh": round(total_energy, 2),
        "total_cost": round(total_cost, 2),
        "top_device": top_device,
        "device_breakdown": device_data,
        "trends": trend,
        "recommendations": reco_list
    }
    
    db_report = Report(
        home_id=data.home_id,
        type=data.type,
        start_date=start_date,
        end_date=end_date,
        content=json.dumps(report_content)
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)

    # Compile bytes and upload to Supabase Storage
    csv_bytes = generate_csv_bytes(report_content)
    pdf_bytes = generate_pdf_bytes(report_content)
    
    csv_url = None
    pdf_url = None
    
    try:
        csv_url = upload_file_to_supabase(csv_bytes, f"report_{db_report.id}.csv", "text/csv")
        pdf_url = upload_file_to_supabase(pdf_bytes, f"report_{db_report.id}.pdf", "application/pdf")
        
        db_report.csv_url = csv_url
        db_report.pdf_url = pdf_url
        db_report.file_path = pdf_url
        db.commit()
        print(f"Report files uploaded to Supabase Storage: CSV={csv_url}, PDF={pdf_url}")
    except Exception as e:
        print(f"Supabase Storage upload failed, using dynamic local endpoints as fallback: {e}")

    return {
        "report_id": db_report.id,
        "summary": report_content,
        "csv_url": csv_url,
        "pdf_url": pdf_url
    }

@router.get("")
def get_reports(home_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_email = current_user["email"]
    home = db.query(Home).filter(Home.id == home_id, Home.user_email == user_email).first()
    if not home:
        raise HTTPException(status_code=403, detail="Access denied")
        
    reports = db.query(Report).filter(Report.home_id == home_id).order_by(Report.created_at.desc()).all()
    return [{
        "id": r.id,
        "type": r.type,
        "start_date": r.start_date,
        "end_date": r.end_date,
        "created_at": r.created_at.replace(tzinfo=timezone.utc).isoformat() if r.created_at else None,
        "pdf_url": r.pdf_url,
        "csv_url": r.csv_url
    } for r in reports]

@router.get("/{report_id}/csv")
def get_report_csv(report_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    user_email = current_user["email"]
    home = db.query(Home).filter(Home.id == report.home_id, Home.user_email == user_email).first()
    if not home:
        raise HTTPException(status_code=403, detail="Access denied")
        
    # If Supabase URL is available, redirect to it
    if report.csv_url:
        return RedirectResponse(url=report.csv_url)
        
    # Fallback to dynamic local generation
    content = json.loads(report.content)
    csv_data = generate_csv_bytes(content)
    
    filename = f"report_{content.get('type')}_{content.get('start_date')}.csv"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    return StreamingResponse(io.BytesIO(csv_data), media_type="text/csv", headers=headers)

@router.get("/{report_id}/pdf")
def get_report_pdf(report_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    user_email = current_user["email"]
    home = db.query(Home).filter(Home.id == report.home_id, Home.user_email == user_email).first()
    if not home:
        raise HTTPException(status_code=403, detail="Access denied")
        
    # If Supabase URL is available, redirect to it
    if report.pdf_url:
        return RedirectResponse(url=report.pdf_url)
        
    # Fallback to dynamic local generation
    content = json.loads(report.content)
    pdf_data = generate_pdf_bytes(content)
    
    filename = f"report_{content.get('type')}_{content.get('start_date')}.pdf"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    return StreamingResponse(io.BytesIO(pdf_data), media_type="application/pdf", headers=headers)
