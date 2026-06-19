from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, ForeignKey, Text
from sqlalchemy.sql import func
from app.db.connection import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    notification_preferences = Column(String, default="all")  # all, email, SMS, none
    created_at = Column(DateTime, server_default=func.now())

class UserSession(Base):
    __tablename__ = "user_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, nullable=False)
    login_time = Column(DateTime, server_default=func.now())
    logout_time = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, server_default=func.now(), onupdate=func.now())
    duration_minutes = Column(Float, nullable=True)

class Home(Base):
    __tablename__ = "homes"
    id = Column(String, primary_key=True, index=True) # e.g. "1", "home_1"
    name = Column(String, nullable=False)
    location = Column(String, nullable=True)
    electricity_rate = Column(Float, default=7.0) # ₹ per kWh
    target_monthly_bill = Column(Float, default=3000.0) # Monthly budget
    home_type = Column(String, default="Apartment") # Apartment, Villa, Independent House, Office
    user_email = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class Device(Base):
    __tablename__ = "devices"
    id = Column(String, primary_key=True, index=True)
    home_id = Column(String, ForeignKey("homes.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    device_type = Column(String, nullable=False)
    brand = Column(String, nullable=True)
    model = Column(String, nullable=True)
    room_name = Column(String, default="Living Room")
    rated_watts = Column(Float, default=100.0)
    installation_date = Column(String, nullable=True)
    status = Column(String, default="OFF")  # ON, OFF
    is_enabled = Column(Boolean, default=True)

class DeviceSession(Base):
    __tablename__ = "device_sessions"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime, server_default=func.now())
    end_time = Column(DateTime, nullable=True)
    runtime_minutes = Column(Float, default=0.0)
    energy_consumed_kwh = Column(Float, default=0.0)
    cost_incurred = Column(Float, default=0.0)

class DeviceDailySummary(Base):
    __tablename__ = "device_daily_summaries"
    id = Column(Integer, primary_key=True, index=True)
    home_id = Column(String, nullable=False)
    device_id = Column(String, nullable=False)
    date = Column(String, nullable=False) # "YYYY-MM-DD"
    runtime_hours = Column(Float, default=0.0)
    energy_consumed_kwh = Column(Float, default=0.0)
    cost_incurred = Column(Float, default=0.0)

class HomeDailySummary(Base):
    __tablename__ = "home_daily_summaries"
    id = Column(Integer, primary_key=True, index=True)
    home_id = Column(String, nullable=False)
    date = Column(String, nullable=False) # "YYYY-MM-DD"
    total_energy_kwh = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)

class HomeBaseline(Base):
    __tablename__ = "home_baselines"
    id = Column(Integer, primary_key=True, index=True)
    home_id = Column(String, nullable=False)
    device_type = Column(String, nullable=False)
    baseline_runtime_hours = Column(Float, default=0.0)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, nullable=False)
    date = Column(String, nullable=False) # "YYYY-MM-DD"
    tomorrow_predicted_hours = Column(Float, default=0.0)
    seven_day_predicted_hours = Column(Float, default=0.0)
    thirty_day_predicted_hours = Column(Float, default=0.0)
    predicted_runtime_hours = Column(Float, default=0.0)
    actual_runtime_hours = Column(Float, default=0.0)
    prediction_accuracy = Column(Float, default=100.0)
    predicted_energy_kwh = Column(Float, default=0.0)
    predicted_cost = Column(Float, default=0.0)

class PredictionResult(Base):
    __tablename__ = "prediction_results"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, nullable=False)
    date = Column(String, nullable=False)
    predicted_runtime = Column(Float, default=0.0)
    actual_runtime = Column(Float, default=0.0)
    error = Column(Float, default=0.0)
    accuracy_percent = Column(Float, default=100.0)

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    home_id = Column(String, nullable=False)
    device_id = Column(String, nullable=True)
    type = Column(String, nullable=False) # "AC Usage", "Target Exceeded", etc.
    message = Column(String, nullable=False)
    potential_saving = Column(Float, default=0.0)
    priority = Column(String, default="medium") # high, medium, low
    created_at = Column(DateTime, server_default=func.now())
    status = Column(String, default="active") # active, dismissed

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    home_id = Column(String, nullable=False)
    type = Column(String, nullable=False) # daily, weekly, monthly
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    content = Column(Text, nullable=False) # JSON string
    file_path = Column(String, nullable=True)
    pdf_url = Column(String, nullable=True)
    csv_url = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    home_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    type = Column(String, default="info") # warning, info, savings
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, nullable=False)
    home_id = Column(String, nullable=False)
    role = Column(String, nullable=False) # user, assistant
    message = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"
    id = Column(Integer, primary_key=True, index=True)
    home_id = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    content_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class TrainingRecord(Base):
    __tablename__ = "training_records"
    id = Column(Integer, primary_key=True, index=True)
    home_id = Column(String, index=True, nullable=False)
    date = Column(String, index=True, nullable=False)
    features_json = Column(Text, nullable=False)
    targets_json = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
