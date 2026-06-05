# 🏥 Healthcare Claims REST API & Analytics Dashboard

![Python](https://img.shields.io/badge/Python-3.14-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![SQLite](https://img.shields.io/badge/Database-SQLite-orange)
![Healthcare](https://img.shields.io/badge/Domain-Healthcare%20IT-purple)

---

## 🎯 Project Overview

A full-stack Healthcare Claims Analytics platform built with 
FastAPI, SQLite, and Streamlit. Ingests real CMS Medicare data 
through an ETL pipeline, exposes analytics via REST API endpoints, 
and visualizes billing anomalies through a live interactive dashboard.

**Live Stats:**
- 📊 50,000 Medicare claims records processed
- 🚨 500 billing anomalies detected
- 💰 $354.52 average Medicare payment gap per claim
- 🔍 Real-time filterable claims explorer

---

## 🏗️ Architecture
CMS Medicare Data (CSV)
↓
ETL Pipeline (Python/Pandas)
↓
SQLite Database
↓
FastAPI REST API (8 endpoints)
↓
Streamlit Dashboard (localhost:8501)


---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| ETL Pipeline | Python, Pandas |
| Database | SQLite, SQLAlchemy |
| REST API | FastAPI, Uvicorn |
| Dashboard | Streamlit, Matplotlib, Seaborn |
| Data Source | CMS Medicare Public Dataset |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API info and endpoint list |
| GET | `/claims` | Paginated claims with filters |
| GET | `/claims/states` | All unique states |
| GET | `/claims/provider-types` | All provider types |
| GET | `/analytics/summary` | Dataset summary metrics |
| GET | `/analytics/top-charging-providers` | Top charging specialties |
| GET | `/analytics/anomalies` | Flagged billing anomalies |
| GET | `/analytics/state-breakdown` | State-level analysis |

---

## 📊 Dashboard Features

- **4 KPI Cards** — Total claims, anomalies, avg charge, payment gap
- **Top Charging Providers** — Bar chart by specialty
- **Billing Anomalies** — Providers flagged above 3x specialty average
- **State Analysis** — Charged vs Medicare paid comparison
- **Claims Explorer** — Filter by state and provider type

---

## 🚀 How To Run

**1. Clone the repo:**
```bash
git clone https://github.com/bhanusravani267/healthcare-claims-api
cd healthcare-claims-api
```

**2. Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

**3. Add sample data to `/data` folder**
Download from: [CMS Medicare Dataset](https://data.cms.gov)

**4. Start the API:**
```bash
PYTHONPATH=. python3 -m uvicorn app.main:app --reload
```

**5. Start the dashboard (new terminal):**
```bash
PYTHONPATH=. streamlit run dashboard/app.py
```

**6. Open:**
- API docs: http://127.0.0.1:8000/docs
- Dashboard: http://localhost:8501

---

## 🔍 Key Findings

- Ambulatory Surgical Centers charge **$8,115 avg** — highest of all specialties
- Average Medicare payment gap is **$354.52 per claim**
- **500+ providers** flagged billing 3x above their specialty average
- Utah and Nebraska show highest average charges among US states

---

## 💼 Business Relevance

Built to mirror real-world Healthcare IT workflows:
- Claims anomaly detection for fraud prevention
- Provider billing pattern analysis for payer organizations
- Medicare payment reconciliation reporting
- Geographic cost variation analysis

---

*Built by Bhanu Mudireddy — Technical BA | Healthcare IT*
*[LinkedIn](https://linkedin.com/in/bhanu-mudireddy) | 
[GitHub](https://github.com/bhanusravani267)*
