📊 Transaction Monitoring & Anomaly Detection System

Real-time transaction monitoring system with anomaly detection, persistence-based alerting, and operational risk visibility.

🧠 Executive Summary (Non-Technical Overview)
This project simulates a real-time monitoring environment for transaction processing systems such as those used by fintechs, payment processors, or acquiring platforms.

The system:

Monitors transaction failure patterns in near real time
Detects statistical anomalies
Measures anomaly persistence over time
Classifies severity levels (INFO → SEVERE)
Triggers automated alerts
Exposes a monitoring API endpoint
Displays operational status in a live dashboard

The goal is to proactively identify service degradation before it evolves into:

Revenue loss
Merchant dissatisfaction
Regulatory risk
Operational crisis

with enough margin to bypass smaller deviations, common outliers present in most operations

This project was built as a portfolio piece aligned with AML Intelligence & Operational Risk monitoring contexts.

🏗 Architecture Overview
Transaction CSV Data
        ↓
FastAPI Monitoring API (/monitor endpoint)
        ↓
Anomaly Model (Z-score + persistence logic)
        ↓
Alert Dispatcher (anti-spam protection)
        ↓
Streamlit Dashboard (real-time visualization)
⚙️ Tech Stack

Python 3.12
FastAPI (Monitoring API)
Streamlit (Dashboard)
Pandas (Data aggregation)
Plotly (Interactive visualization)
Uvicorn (ASGI server)

🚨 Monitoring Model

1️⃣ Statistical Detection

For each metric:

failed_rate
denied_rate
reversed_rate

Threshold is calculated as:
mean + 3 * standard deviation

This allows dynamic anomaly detection instead of static rule-based thresholds.

2️⃣ Persistence-Based Severity Model

Anomalies only trigger alerts if they persist over time:

Persistence Severity
≥ 15 min  INFO
≥ 30 min  WARNING
≥ 45 min  CRITICAL
≥ 60 min  SEVERE

This avoids noise and prevents false positives.

3️⃣ Anti-Spam Alert Logic

Alerts are dispatched only if:
Severity != HEALTHY

The same severity for the same metric was not recently triggered

Alerts are logged in:
alert_log.json

This simulates production-grade alert persistence.

📊 Dashboard Features

Time window filtering (6h, 12h, 24h, 48h, full period)
Consolidated anomaly visualization
Real-time API connection
Severity badges
Alert display panel
Persistence detail breakdown per metric

📡 API Endpoint
GET /monitor

Returns:

{
  "current_minute": "...",
  "metrics": {...},
  "thresholds": {...},
  "persistence_analysis": {...}
}

This endpoint simulates integration with:

Monitoring platforms
Incident systems
Notification services
AML risk engines

🗄 SQL Monitoring Query

The project includes SQL queries inside:

queries/

Used to aggregate:
Total transactions
Failed / Denied / Reversed counts
Minute-level aggregation

This simulates production database usage instead of CSV files.


▶️ How to Run the Project

#can be done on a virtual environment for test, highly suggested by the way
for that enter on the root folder of the project and run on terminal:

python -m venv venv

Then run:
venv\Scripts\activate 
venv created and active

1️⃣ Install dependencies
pip install -r requirements.txt

2️⃣ Start Monitoring API
From project root:
uvicorn app.main:app --reload

API runs at:
http://127.0.0.1:8000

3️⃣ Start Dashboard
In a new terminal:
streamlit run dashboard/app.py

Dashboard runs at:
http://localhost:8501

Short explanation:
1. Run on root folder: python -m venv venv
2. Then run: venv\Scripts\activate  
3. then run: pip install -r requirements.txt  
4. Run API first on your terminal by running: uvicorn app.main:app --reload 
`(on browser you can see it on http://127.0.0.1:8000/docs#/default/monitor_monitor_get)`
5. Then run scipt of the dashboard on a second terminal fron the root directory of the project: streamlit run dashboard/app.py 
`(and it will be available on http://localhost:8501 on your browser)`

📁 Project Structure
app/
  ├── main.py
  ├── api/
  │     └── routes.py
  └── services/
        └── alert_dispatcher.py

dashboard/
  └── app.py

data/
  └── transactions.csv

queries/
  └── monitoring_queries.sql

requirements.txt
LICENSE
README.md

🔎 Opportunities for Improvement
During development, several structural opportunities were identified:

1️⃣ Missing Transaction Dimensions

Dataset lacks:
channel
product
acquirer
card_type

With these fields we could implement:

Channel-level anomaly detection
Product-level failure monitoring
Acquirer degradation tracking
Card scheme performance analysis

2️⃣ No Latency Metrics

Ideal dataset would include:
request_timestamp
response_timestamp
duration_ms

This would allow:

SLA breach detection
Latency anomaly modeling
Infrastructure bottleneck analysis

3️⃣ Baseline Model Improvements

Current model:
Mean + 3σ
Short-term historical baseline

Future improvements:

Seasonal baseline (hour-of-day)
EWMA models
ARIMA forecasting
ML-based anomaly detection

4️⃣ Real Streaming Data

Current system uses static CSV.

Production version should:
Consume Kafka stream
Or subscribe to message queue
Or connect directly to database

🛡 AML Context & Revenue Risk

Although this project focuses on operational monitoring, it directly intersects with AML and financial risk.

Why This Matters:
1️⃣ Revenue Protection

High failed/denied rates:
Reduce transaction approval
Decrease merchant revenue
Impact company earnings

2️⃣ Fraud & AML Signals

Abnormal spikes in:

Denied transactions
Reversed transactions

May indicate:

Fraud attempts
Chargeback abuse
Bot attacks
Testing of stolen cards

Monitoring these anomalies supports:

Fraud prevention
AML investigations
Risk escalation workflows

3️⃣ Regulatory Exposure

Persistent degradation:

May violate SLA agreements
May impact regulated financial operations
Could trigger compliance incidents

🎯 Why This Project Matters

This system demonstrates:

Statistical reasoning
Operational monitoring design
Backend API construction
Alert lifecycle logic
Risk prioritization framework
AML-adjacent thinking
Revenue impact awareness

It bridges:

Data Analysis
Backend Engineering
Operational Risk
Financial Monitoring

🚀 Future Roadmap (TBD?)

Email alert integration
Slack / webhook notifications
Database integration (PostgreSQL)
Historical alert dashboard
Risk scoring engine
Deployment via Docker
Cloud deployment (AWS/GCP/Azure)

👤 Author

Leonardo Lima
Aspiring AML Intelligence Analyst
Focused on operational risk & transaction monitoring systems

📜 License
MIT License
