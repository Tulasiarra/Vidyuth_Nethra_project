# ⚡ Vidyuth Nethra – AI Powered Home Energy Management System

## 📌 Project Overview

Vidyuth Nethra is an AI-powered Home Energy Management System designed to help households monitor, analyze, predict, and optimize electricity consumption.

The system combines:

- 🔐 User Authentication
- 🏠 Household Management
- ⚡ Appliance Energy Tracking
- 📊 Energy Consumption Analytics
- 🤖 Machine Learning-Based Energy Prediction
- 💡 Intelligent Energy Saving Recommendations
- ☁️ Supabase Cloud Database

The primary objective is to predict future electricity consumption and provide actionable recommendations to reduce energy usage and electricity bills.

---

# 🚀 Features

## User Management

- User Registration
- User Login
- JWT Authentication
- Protected APIs

## Household Management

- Create Household
- View Household Details
- Select Active Household
- Switch Household Sessions

## Appliance Management

- Add Appliances
- Track Appliance Usage
- Monitor Consumption Patterns
- Energy Rating Tracking

## Energy Analytics

- Monthly Consumption Tracking
- Appliance-wise Energy Contribution
- Bill Estimation
- Consumption Summary

## AI / ML Features

### Energy Consumption Prediction

Predicts future electricity usage based on:

- Appliance Wattage
- Quantity
- Daily Usage Hours
- Month
- Energy Rating

### Recommendation Engine

Provides suggestions such as:

- Reduce appliance usage
- Replace old appliances
- Upgrade to higher energy rating appliances
- Prevent future high electricity bills

---

# 🏗️ System Architecture

```text
Frontend
    ↓
FastAPI Backend
    ↓
Supabase Database
    ↓
Machine Learning Module
    ↓
Prediction Engine
    ↓
Recommendation Engine
```

---

# 🛠️ Tech Stack

## Frontend

- React.js
- Tailwind CSS
- Chart.js

## Backend

- FastAPI
- Python 3.11

## Database

- Supabase
- PostgreSQL

## Authentication

- JWT Tokens
- OAuth2 Password Bearer

## Machine Learning

- Scikit-Learn
- Random Forest Regressor
- Pandas
- NumPy
- Joblib

---

# 📂 Project Structure

```text
backend/
│
├── app/
│   ├── routes.py
│   ├── service.py
│   ├── auth_schema.py
│   ├── auth_middleware.py
│   ├── database.py
│   ├── config.py
│   └── main.py
│
├── sessions/
│   ├── routes.py
│   ├── service.py
│   ├── lifecycle.py
│   └── schema.py
│
├── energy/
│   ├── routes.py
│   ├── service.py
│   ├── schema.py
│   └── recommendation.py
│
├── ml/
│   ├── train_model.py
│   ├── predict.py
│   ├── recommender.py
│   ├── energy_model.pkl
│   └── dataset/
│       ├── energydata_complete.csv
│       └── prepared_dataset.csv
│
└── requirements.txt
```

---

# 🗄️ Database Schema

## Users

```sql
users
```

Stores registered users.

---

## Households

```sql
households
```

Stores household information.

---

## Appliances

```sql
appliances
```

Stores appliance master data.

---

## User Appliances

```sql
user_appliances
```

Maps appliances to households.

---

## Appliance Usage

```sql
appliance_usage
```

Stores monthly energy usage records.

---

## User Bills

```sql
user_bills
```

Stores electricity bill information.

---

## Recommendation History

```sql
recommendation_history
```

Stores generated recommendations.

---

# 🤖 Machine Learning Module

## Dataset

Dataset Used:

**Appliances Energy Prediction Dataset**

Source:

https://raw.githubusercontent.com/LuisM78/Appliances-energy-prediction-data/master/energydata_complete.csv

---

## Feature Engineering

Features:

```python
avg_wattage
quantity
average_daily_hours
month
energy_rating
```

Target:

```python
estimated_units_consumed
```

---

## Model

```python
RandomForestRegressor
```

---

## Evaluation Metrics

- R² Score
- Mean Absolute Error (MAE)

Results are stored in:

```text
evaluation_metrics.txt
```

---

# 🔮 Prediction Workflow

```text
Household Data
      ↓
Appliance Usage
      ↓
Feature Generation
      ↓
Random Forest Model
      ↓
Predicted Energy Consumption
      ↓
Predicted Electricity Bill
```

API:

```http
GET /energy/prediction/{household_id}
```

Example Response:

```json
{
  "household_id": "uuid",
  "predicted_units": 425.8,
  "predicted_bill": 3832.2
}
```

---

# 💡 Recommendation Engine

Business Rules:

### High Consumption

```python
predicted_units > 300
```

Recommendation:

```text
Reduce appliance usage
```

---

### Low Energy Rating

```python
energy_rating < 3
```

Recommendation:

```text
Upgrade to 5-Star appliance
```

---

### Old Appliance

```python
appliance_age > 8 years
```

Recommendation:

```text
Replace old appliance
```

---

### High Future Bill

```python
predicted_bill > historical_average
```

Recommendation:

```text
Expected high bill next month
```

API:

```http
GET /energy/recommendations/{household_id}
```

---

# 🔐 Authentication APIs

## Register

```http
POST /register
```

---

## Login

```http
POST /login
```

---

## OAuth2 Token

```http
POST /token
```

---

## Profile

```http
GET /profile
```

---

# 🏠 Session APIs

## Select Household

```http
POST /sessions/select
```

---

## Switch Household

```http
POST /sessions/switch
```

---

## Session Status

```http
GET /sessions/status
```

---

## End Session

```http
POST /sessions/end
```

---

# ⚡ Energy APIs

## Energy Data

```http
GET /energy/data
```

---

## Energy Summary

```http
GET /energy/summary
```

---

## Hourly Usage

```http
GET /energy/hourly
```

---

## Energy Prediction

```http
GET /energy/prediction/{household_id}
```

---

## Recommendations

```http
GET /energy/recommendations/{household_id}
```

---

# ☁️ Supabase Integration

Environment Variables:

```env
SUPABASE_URL=your_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

SECRET_KEY=your_secret_key
ALGORITHM=HS256
```

---

# ▶️ Running the Project

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Train ML Model

```bash
python backend/ml/train_model.py
```

---

## Start Backend

```bash
cd backend/app

uvicorn main:app --reload
```

---

## Open Swagger UI

```text
http://127.0.0.1:8000/docs
```

---

# 📊 Current Project Status

| Module | Status |
|----------|----------|
| Authentication | ✅ Complete |
| Session Management | ✅ Complete |
| Supabase Integration | ✅ Complete |
| Energy Tracking | ✅ Complete |
| Dataset Preparation | ✅ Complete |
| ML Model Training | ✅ Complete |
| Energy Prediction | ✅ Complete |
| Recommendation Engine | ✅ Complete |
| Recommendation History | ✅ Complete |
| Bill Forecasting | ✅ Complete |
| Frontend Integration | 🔄 In Progress |
| Deployment | 🔄 Pending |

---

# 👨‍💻 Team Contributions

### Backend Member 1

- Authentication
- JWT Security
- User Management
- Supabase User Integration

### Backend Member 2

- Session Management
- Household Management
- Session Lifecycle APIs

### Backend Member 3

- Energy Module
- ML Integration
- Prediction APIs
- Recommendation Engine
- Recommendation History

---

# 🎯 Future Enhancements

- Real-Time Smart Meter Integration
- IoT Device Connectivity
- LSTM-Based Forecasting
- Electricity Tariff Optimization
- Mobile Application
- Energy Consumption Alerts
- Carbon Footprint Analysis

---

## 📄 License

This project is developed for academic and research purposes.

---

### ⚡ Vidyuth Nethra

**"Predict. Optimize. Save Energy."**