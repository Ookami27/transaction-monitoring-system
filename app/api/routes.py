from app.services.alert_dispatcher import dispatch_alert
from fastapi import APIRouter
import pandas as pd
import numpy as np
from datetime import datetime

router = APIRouter()

# =========================
# CONFIG
# =========================

DATA_PATH = "data/transactions.csv"


# =========================
# SEVERITY LOGIC
# =========================

def calculate_severity(consecutive_minutes):
    if consecutive_minutes >= 60:
        return "SEVERE"
    elif consecutive_minutes >= 45:
        return "CRITICAL"
    elif consecutive_minutes >= 30:
        return "WARNING"
    elif consecutive_minutes >= 15:
        return "INFO"
    else:
        return "HEALTHY"


def dispatch_alert(metric_name, severity, value):
    if severity != "HEALTHY":
        print(f"[ALERT] {metric_name} | Severity: {severity} | Current value: {value}")


# =========================
# MONITOR ENDPOINT
# =========================

@router.get("/monitor")
def monitor():

    df = pd.read_csv(DATA_PATH)

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    # Agregação por minuto
    df_minute = df.groupby(pd.Grouper(key="timestamp", freq="1min")).agg(
        total_tx=("status", "count"),
        failed=("status", lambda x: (x == "failed").sum()),
        denied=("status", lambda x: (x == "denied").sum()),
        reversed=("status", lambda x: (x == "reversed").sum()),
    ).reset_index()

    df_minute["failed_rate"] = df_minute["failed"] / df_minute["total_tx"]
    df_minute["denied_rate"] = df_minute["denied"] / df_minute["total_tx"]
    df_minute["reversed_rate"] = df_minute["reversed"] / df_minute["total_tx"]

    df_minute.fillna(0, inplace=True)

    # Último minuto
    current = df_minute.iloc[-1]

    # Thresholds estatísticos
    failed_threshold = df_minute["failed_rate"].mean() + 3 * df_minute["failed_rate"].std()
    denied_threshold = df_minute["denied_rate"].mean() + 3 * df_minute["denied_rate"].std()
    reversed_threshold = df_minute["reversed_rate"].mean() + 3 * df_minute["reversed_rate"].std()

    # Persistência simples (conta minutos consecutivos acima do threshold)
    def persistence(metric, threshold):
        consecutive = 0
        for value in reversed(df_minute[metric].tolist()):
            if value > threshold:
                consecutive += 1
            else:
                break
        return consecutive

    failed_persistence = persistence("failed_rate", failed_threshold)
    denied_persistence = persistence("denied_rate", denied_threshold)
    reversed_persistence = persistence("reversed_rate", reversed_threshold)

    # Severidade
    failed_severity = calculate_severity(failed_persistence)
    denied_severity = calculate_severity(denied_persistence)
    reversed_severity = calculate_severity(reversed_persistence)

    # Dispatch automático
    dispatch_alert("FAILED_RATE", failed_severity, failed_persistence)
    dispatch_alert("DENIED_RATE", denied_severity, denied_persistence)
    dispatch_alert("REVERSED_RATE", reversed_severity, reversed_persistence)

    return {
        "current_minute": str(current["timestamp"]),
        "metrics": {
            "failed_rate": float(current["failed_rate"]),
            "denied_rate": float(current["denied_rate"]),
            "reversed_rate": float(current["reversed_rate"]),
        },
        "thresholds": {
            "failed": float(failed_threshold),
            "denied": float(denied_threshold),
            "reversed": float(reversed_threshold),
        },
        "persistence_analysis": {
            "failed": {
                "consecutive_minutes": failed_persistence,
                "severity": failed_severity
            },
            "denied": {
                "consecutive_minutes": denied_persistence,
                "severity": denied_severity
            },
            "reversed": {
                "consecutive_minutes": reversed_persistence,
                "severity": reversed_severity
            }
        }
    }