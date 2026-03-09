from pydantic import BaseModel
from typing import Literal
from datetime import datetime
from app.services.alert_dispatcher import dispatch_alert
from fastapi import APIRouter
import pandas as pd
from app.core.store import append_transaction, get_transactions
 
router = APIRouter()

class TransactionIn(BaseModel):
    timestamp: datetime
    status: Literal["approved", "failed", "denied", "reversed"]
    count: int

DATA_PATH = "data/transactions_anomaly.csv"


def calculate_severity(consecutive_minutes: int) -> str:
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


def persistence(series: pd.Series, threshold: float) -> int:
    """
    Conta quantos minutos consecutivos, a partir do final da série,
    a métrica ficou acima do threshold.
    """
    consecutive = 0
    for value in reversed(series.tolist()):
        if value > threshold:
            consecutive += 1
        else:
            break
    return consecutive


@router.post("/ingest-transaction")
def ingest_transaction(tx: TransactionIn):
    payload = {
        "timestamp": tx.timestamp,
        "status": tx.status,
        "count": tx.count,
    }

    append_transaction(payload)

    return {"status": "ok", "stored": payload}


@router.get("/monitor")
def monitor():

    live_txs = get_transactions()

    if live_txs:
        df = pd.DataFrame(live_txs)
    else:
        df = pd.read_csv(DATA_PATH)

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    df_pivot = (
        df.pivot_table(
            index="timestamp",
            columns="status",
            values="count",
            aggfunc="sum"
        )
        .fillna(0)
    )

    for col in ["failed", "denied", "reversed"]:
        if col not in df_pivot.columns:
            df_pivot[col] = 0

    df_pivot["total_tx"] = df_pivot.sum(axis=1)
    total_safe = df_pivot["total_tx"].replace(0, pd.NA)

    df_pivot["failed_rate"] = (df_pivot["failed"] / total_safe).fillna(0)
    df_pivot["denied_rate"] = (df_pivot["denied"] / total_safe).fillna(0)
    df_pivot["reversed_rate"] = (df_pivot["reversed"] / total_safe).fillna(0)

    current = df_pivot.iloc[-1]
    current_ts = df_pivot.index[-1]

    failed_threshold = df_pivot["failed_rate"].mean() + 3 * df_pivot["failed_rate"].std()
    denied_threshold = df_pivot["denied_rate"].mean() + 3 * df_pivot["denied_rate"].std()
    reversed_threshold = df_pivot["reversed_rate"].mean() + 3 * df_pivot["reversed_rate"].std()

    failed_persistence = persistence(df_pivot["failed_rate"], failed_threshold)
    denied_persistence = persistence(df_pivot["denied_rate"], denied_threshold)
    reversed_persistence = persistence(df_pivot["reversed_rate"], reversed_threshold)

    failed_severity = calculate_severity(failed_persistence)
    denied_severity = calculate_severity(denied_persistence)
    reversed_severity = calculate_severity(reversed_persistence)

    try:
        dispatch_alert("FAILED_RATE", failed_severity, failed_persistence)
        dispatch_alert("DENIED_RATE", denied_severity, denied_persistence)
        dispatch_alert("REVERSED_RATE", reversed_severity, reversed_persistence)
    except Exception as e:
        print("Error in dispatch_alert:", e)

    return {
        "current_minute": str(current_ts),
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
                "severity": failed_severity,
            },
            "denied": {
                "consecutive_minutes": denied_persistence,
                "severity": denied_severity,
            },
            "reversed": {
                "consecutive_minutes": reversed_persistence,
                "severity": reversed_severity,
            },
        },
    }