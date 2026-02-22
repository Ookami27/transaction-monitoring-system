import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import os
import json
from datetime import timedelta

st.title("📊 Transaction Monitoring Dashboard")

# =========================
# LOAD DATA
# =========================

df_raw = pd.read_csv("data/transactions.csv")
df_raw["timestamp"] = pd.to_datetime(df_raw["timestamp"])

df_pivot = (
    df_raw
    .pivot(index="timestamp", columns="status", values="count")
    .fillna(0)
)

df_pivot["total"] = df_pivot.sum(axis=1)

df_pivot["failed_rate"] = df_pivot.get("failed", 0) / df_pivot["total"]
df_pivot["denied_rate"] = df_pivot.get("denied", 0) / df_pivot["total"]
df_pivot["reversed_rate"] = df_pivot.get("reversed", 0) / df_pivot["total"]

df = df_pivot.reset_index()

# =========================
# TIME FILTER DROPDOWN
# =========================

st.subheader("📅 Time Filter")

options = {
    "Last 6 hours": 6,
    "Last 12 hours": 12,
    "Last 24 hours": 24,
    "Last 48 hours": 48,
    "Full Period": None
}

selected_option = st.selectbox("Select time window:", list(options.keys()))

if options[selected_option] is not None:
    hours = options[selected_option]
    end_time = df["timestamp"].max()
    start_time = end_time - timedelta(hours=hours)
    df_filtered = df[df["timestamp"] >= start_time]
else:
    df_filtered = df.copy()

# =========================
# CONSOLIDATED GRAPH
# =========================

st.subheader("📈 Consolidated Transaction Rates")

fig = go.Figure()

for metric in ["failed_rate", "denied_rate", "reversed_rate"]:
    fig.add_trace(
        go.Scatter(
            x=df_filtered["timestamp"],
            y=df_filtered[metric],
            mode="lines",
            name=metric
        )
    )

fig.update_layout(
    xaxis_title="Timestamp",
    yaxis_title="Rate",
)

st.plotly_chart(fig, width="stretch")

# =========================
# REAL-TIME MONITORING
# =========================

st.subheader("🚨 Real-Time Monitoring Status")

API_URL = "http://127.0.0.1:8000/monitor"

try:
    response = requests.get(API_URL)
    data = response.json()

    persistence = data["persistence_analysis"]

    severity_levels = []

    for metric in ["failed", "denied", "reversed"]:
        severity_levels.append(persistence[metric]["severity"])

    if "SEVERE" in severity_levels:
        st.error("🔥 CRISIS: Persistent anomaly detected for 60+ minutes!")
    elif "CRITICAL" in severity_levels:
        st.error("🔴 CRITICAL: 45+ minutes of anomaly")
    elif "WARNING" in severity_levels:
        st.warning("🟡 WARNING: 30+ minutes of anomaly")
    elif "INFO" in severity_levels:
        st.warning("🟡 Early anomaly detected (15+ min)")
    else:
        st.success("🟢 System Healthy")

    st.markdown("### Persistence Details")

    for metric in ["failed", "denied", "reversed"]:
        consecutive = persistence[metric]["consecutive_minutes"]
        severity = persistence[metric]["severity"]

        col1, col2, col3 = st.columns([2,1,1])

        with col1:
            st.write(f"**{metric.upper()}**")

        with col2:
            st.write(f"Minutes Above Threshold: {consecutive}")

        with col3:
            if severity == "HEALTHY":
                st.success("Healthy")
            elif severity == "INFO":
                st.info("INFO (15m)")
            elif severity == "WARNING":
                st.warning("WARNING (30m)")
            elif severity == "CRITICAL":
                st.error("CRITICAL (45m)")
            elif severity == "SEVERE":
                st.error("SEVERE (60m)")

except Exception as e:
    st.error("Could not connect to Monitoring API")
    st.write(str(e))

st.subheader("🚨 Active Alerts")

ALERT_FILE = "alert_log.json"

if os.path.exists(ALERT_FILE):
    with open(ALERT_FILE, "r") as f:
        alerts = json.load(f)

    if alerts:
        latest_alert = alerts[-1]

        severity = latest_alert["severity"]

        if severity in ["WARNING"]:
            st.warning(latest_alert["message"])
        elif severity in ["CRITICAL", "SEVERE"]:
            st.error(latest_alert["message"])
        else:
            st.info(latest_alert["message"])

    else:
        st.success("No active alerts.")
else:
    st.success("No alerts generated yet.")