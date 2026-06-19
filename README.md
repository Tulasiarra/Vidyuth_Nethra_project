# Vidyuth Nethra (विद्युत् नेत्र)

An AI-powered smart energy monitoring, forecasting, and voice-controlled smart home assistant inspired by modern home hubs. **Vidyuth Nethra** helps users manage and optimize their domestic electricity consumption, identify high-consumption appliances, receive personalized energy recommendations, and predict monthly utility bills using advanced Machine Learning (LSTM).

---

## 📋 Table of Contents
- [🌟 Key Features](#-key-features)
- [🏗️ System Architecture](#️-system-architecture)
  - [Frontend Hub](#frontend-hub)
  - [FastAPI Backend](#fastapi-backend)
  - [Machine Learning Engine](#machine-learning-engine)
  - [GenAI RAG Chatbot](#genai-rag-chatbot)
  - [Voice Intent Classification](#voice-intent-classification)
  - [PDF/CSV Report Generation](#pdfcsv-report-generation)
- [🗄️ Database Schema & Models](#️-database-schema--models)
- [⚙️ Environment Configuration](#️-environment-configuration)
- [🚀 Getting Started](#-getting-started)
  - [1. Backend Setup](#1-backend-setup)
  - [2. Frontend Setup](#2-frontend-setup)
  - [3. Running the Services](#3-running-the-services)
- [🐳 Docker Deployment](#-docker-deployment)
- [📊 Datasets & Seeding](#-datasets-&-seeding)

---

## 🌟 Key Features
- **Smart Dashboard**: View real-time electricity consumption, cost metrics, monthly targets, and live device status.
- **AI-Powered Forecasting**: Predict daily, weekly, and 30-day runtimes and costs using a TensorFlow Long Short-Term Memory (LSTM) model.
- **Natural Language Voice Assistant**: Control devices and query energy consumption metrics using a speech intent classifier powered by LLMs.
- **RAG Chatbot ("Vidhyuth Netra")**: Engage with a smart assistant using a Retrieval-Augmented Generation pipeline built with LangChain, Groq (Llama-3.3-70b-versatile), and live database context.
- **Exceeded Budget Notifications**: Automatically detect when projected bills exceed monthly targets and alert the user via dashboard notifications and SMTP emails.
- **Reports Export**: Generate detailed energy reports and download them as custom-styled PDFs (compiled via ReportLab) or CSVs uploaded to Supabase Storage.
- **Personalized Machine Learning Training**: Retrain the forecasting models globally or specifically for individual households using historical device-level summaries.

---

## 🏗️ System Architecture

### Frontend Hub
- **Framework**: React 19 bootstrapped with Vite.
- **Visualizations**: Recharts for dynamic time-series charts, runtime distribution pie charts, and monthly goal trackers.
- **Design System**: A responsive dashboard interface with styled navigation, modular layouts, and notification controls.
- **Entrypoints**: [Dashboard.jsx](file:///c:/Users/Varsha/Downloads/Vidyuth_Nethra_project%20(1)/Vidyuth_Nethra_project/frontend/src/pages/Dashboard.jsx), [DevicesPage.jsx](file:///c:/Users/Varsha/Downloads/Vidyuth_Nethra_project%20(1)/Vidyuth_Nethra_project/frontend/src/pages/DevicesPage.jsx), [EnergyPage.jsx](file:///c:/Users/Varsha/Downloads/Vidyuth_Nethra_project%20(1)/Vidyuth_Nethra_project/frontend/src/pages/EnergyPage.jsx), [ChatPage.jsx](file:///c:/Users/Varsha/Downloads/Vidyuth_Nethra_project%20(1)/Vidyuth_Nethra_project/frontend/src/pages/ChatPage.jsx).

### FastAPI Backend
- **Framework**: FastAPI (Python 3.11).
- **ORM & DB**: SQLAlchemy connecting to a PostgreSQL instance hosted on Supabase.
- **Security**: JWT-based authentication with token verification middleware and bcrypt password hashing.
- **Entrypoint**: [main.py](file:///c:/Users/Varsha/Downloads/Vidyuth_Nethra_project%20(1)/Vidyuth_Nethra_project/backend/app/main.py).

### Machine Learning Engine
- **Model**: TensorFlow Keras LSTM neural network mapping 30 days of runtime history across 24 device categories to predict next-day runtime.
- **Device Categories**: `ac`, `fan`, `bldc_fan`, `cooler`, `fridge`, `tv`, `light`, `led_light`, `washing_machine`, `geyser`, `microwave`, `oven`, `computer`, `laptop`, `monitor`, `router`, `water_purifier`, `dishwasher`, `mixer`, `induction_stove`, `air_purifier`, `vacuum_cleaner`, `iron_box`, `water_pump`.
- **Inference**: Dynamically falls back to a smart moving average when the LSTM model is not trained or loaded.
- **Scripts**: [predict.py](file:///c:/Users/Varsha/Downloads/Vidyuth_Nethra_project%20(1)/Vidyuth_Nethra_project/backend/ml/predict.py) & [train.py](file:///c:/Users/Varsha/Downloads/Vidyuth_Nethra_project%20(1)/Vidyuth_Nethra_project/backend/ml/train.py).

### GenAI RAG Chatbot
- **Framework**: LangChain combined with the Groq API (`llama-3.3-70b-versatile`).
- **Context Construction**: Formulates a detailed markdown document detailing today's usage, device inventory, 10-day summaries, forecasting accuracy, active opportunities, and uploaded knowledge manuals, feeding it as context to the assistant.
- **API File**: [chatbot.py](file:///c:/Users/Varsha/Downloads/Vidyuth_Nethra_project%20(1)/Vidyuth_Nethra_project/backend/app/api/chatbot.py).

### Voice Intent Classification
- **Mechanism**: Classifies commands using Groq `llama-3.1-8b-instant` to output a structured JSON response specifying the intent (e.g., `toggle_on`, `toggle_off`, `query_usage`, `query_bill`, `query_top_device`, `query_prediction`) along with parameter details (`device_type`, `room_name`).
- **API File**: [voice.py](file:///c:/Users/Varsha/Downloads/Vidyuth_Nethra_project%20(1)/Vidyuth_Nethra_project/backend/app/api/voice.py).

### PDF/CSV Report Generation
- **Libraries**: ReportLab for styling and generating PDF pages containing tabular device summaries, consumption costs, and AI energy recommendations.
- **Storage**: Reports are uploaded to Supabase Storage. The backend implements fallback endpoints to directly stream raw files locally in case of upload failure.
- **API File**: [reports.py](file:///c:/Users/Varsha/Downloads/Vidyuth_Nethra_project%20(1)/Vidyuth_Nethra_project/backend/app/api/reports.py).

---

## 🗄️ Database Schema & Models

Below is the database model mapping implemented in [models.py](file:///c:/Users/Varsha/Downloads/Vidyuth_Nethra_project%20(1)/Vidyuth_Nethra_project/backend/app/db/models.py):

| Class Name | Table Name | Key Columns | Purpose |
|---|---|---|---|
| `User` | `users` | `id`, `name`, `email`, `password_hash`, `notification_preferences` | User profiles and credentials. |
| `UserSession` | `user_sessions` | `id`, `user_email`, `login_time`, `duration_minutes` | Track active user login durations. |
| `Home` | `homes` | `id`, `name`, `location`, `electricity_rate`, `target_monthly_bill` | Properties of the monitored household. |
| `Device` | `devices` | `id`, `home_id`, `name`, `device_type`, `rated_watts`, `status` | Individual smart appliances. |
| `DeviceSession` | `device_sessions` | `id`, `device_id`, `start_time`, `runtime_minutes`, `energy_consumed_kwh` | Live runtime tracking of active devices. |
| `DeviceDailySummary` | `device_daily_summaries` | `id`, `device_id`, `date`, `runtime_hours`, `energy_consumed_kwh` | Consolidated daily appliance statistics. |
| `HomeDailySummary` | `home_daily_summaries` | `id`, `home_id`, `date`, `total_energy_kwh`, `total_cost` | Consolidated daily home-level statistics. |
| `HomeBaseline` | `home_baselines` | `id`, `home_id`, `device_type`, `baseline_runtime_hours` | Baseline average consumption values. |
| `Prediction` | `predictions` | `id`, `device_id`, `date`, `tomorrow_predicted_hours`, `predicted_cost` | Model predictions and tracking. |
| `PredictionResult` | `prediction_results` | `id`, `device_id`, `date`, `predicted_runtime`, `accuracy_percent` | Tracks accuracy against actual usage. |
| `Recommendation` | `recommendations` | `id`, `home_id`, `type`, `message`, `potential_saving`, `status` | Energy-saving optimizations. |
| `Report` | `reports` | `id`, `home_id`, `type`, `content`, `pdf_url`, `csv_url` | Exported energy analysis report records. |
| `Notification` | `notifications` | `id`, `home_id`, `title`, `message`, `type`, `is_read` | Alerts (e.g., budget limit exceeded warnings). |
| `ChatHistory` | `chat_history` | `id`, `user_email`, `home_id`, `role`, `message` | Logs the LLM chat history. |
| `TrainingRecord` | `training_records` | `id`, `home_id`, `date`, `features_json`, `targets_json` | Retraining datasets loaded into SQL. |
| `RegistrationOTP` | `registration_otps` | `id`, `email`, `otp`, `created_at` | Registration flow verification. |
| `PasswordResetOTP` | `password_reset_otps` | `id`, `email`, `otp`, `created_at` | Password recovery verification. |

---

## ⚙️ Environment Configuration

To configure the application, create a `.env` file in the root directory. 

```env
# Supabase & Connection Configurations
NEXT_PUBLIC_SUPABASE_URL=https://<project-ref>.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=sb_publishable_...
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_KEY=sb_publishable_...
DATABASE_URL=postgresql://postgres.<project-ref>:<password>@<pooler-host>:6543/postgres

# Generative AI Config
GROQ_API_KEY=gsk_...

# LangChain Tracing (Optional)
LANGCHAIN_API_KEY="lsv2_pt_..."
LANGCHAIN_PROJECT="tracing_langsmith"

# Google Auth (Optional)
GOOGLE_CLIENT_ID=<id>.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-...

# SMTP Configurations for Email Alerts
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=vidyuthnethra@gmail.com
SMTP_PASSWORD=<app-password>
SMTP_FROM=vidyuthnethra@gmail.com
```

---

## 🚀 Getting Started

### 📋 Prerequisites
- **Python**: 3.11+
- **Node.js**: 18+ (with npm)
- **PostgreSQL**: Managed Supabase instance

---

### 1. Backend Setup

From the root directory, create a virtual environment and install dependencies:

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

#### Database Seeding
Upon launching the backend, database tables are automatically initialized and populated using CSV files located in `backend/dataset/`. To run the seed script manually:

```powershell
python backend/app/db/seed.py
```

*Note: Default seeded credentials are:*
- **Email**: `arjun@example.com`
- **Password**: `demo1234`

---

### 2. Frontend Setup

Navigate to the frontend folder and install npm packages:

```powershell
cd frontend
npm install
```

---

### 3. Running the Services

#### Run the FastAPI Backend
Start the server using `uvicorn`:

```powershell
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Run the Vite Frontend
Start the React application dev server:

```powershell
cd frontend
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🐳 Docker Deployment

The application includes a [Dockerfile](file:///c:/Users/Varsha/Downloads/Vidyuth_Nethra_project%20(1)/Vidyuth_Nethra_project/Dockerfile) for building and deploying the backend service.

```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=7860
EXPOSE 7860
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT}"]
```

To run the container locally:

```powershell
docker build -t vidyuth-nethra-backend .
docker run -p 7860:7860 --env-file .env vidyuth-nethra-backend
```

---

## 📊 Datasets & Seeding

The application imports initial operational values and training parameters from the CSV files in `backend/dataset/`:
- **[homes.csv](file:///c:/Users/Varsha/Downloads/Vidyuth_Nethra_project%20(1)/Vidyuth_Nethra_project/backend/dataset/homes.csv)**: Sets target monthly budget and electrical units cost values.
- **[devices.csv](file:///c:/Users/Varsha/Downloads/Vidyuth_Nethra_project%20(1)/Vidyuth_Nethra_project/backend/dataset/devices.csv)**: Populates lists of appliances, brands, rated wattage, and rooms.
- **[device_daily_summary.csv](file:///c:/Users/Varsha/Downloads/Vidyuth_Nethra_project%20(1)/Vidyuth_Nethra_project/backend/dataset/device_daily_summary.csv)**: Backfills historical device usage records to establish user baselines.
- **[training_dataset.csv](file:///c:/Users/Varsha/Downloads/Vidyuth_Nethra_project%20(1)/Vidyuth_Nethra_project/backend/dataset/training_dataset.csv)**: Provides feature-engineered outputs to train the LSTM models.
