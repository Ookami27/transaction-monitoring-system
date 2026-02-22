import numpy as np

def z_score(value, mean, std):
    if std == 0:
        return 0
    return (value - mean) / std

def detect_anomaly(data):

    failed_rate = data["failed_rate"]
    denied_rate = data["denied_rate"]
    reversed_rate = data["reversed_rate"]

    # Regras fixas (rule-based)
    rules_triggered = (
        failed_rate > 0.05 or
        denied_rate > 0.07 or
        reversed_rate > 0.03
    )

    # Modelo estatístico (score-based)
    z_failed = z_score(failed_rate, data["mean_failed"], data["std_failed"])
    score_triggered = abs(z_failed) > 3

    alert = rules_triggered or score_triggered

    return {
    "alert": bool(alert),
    "rules_triggered": bool(rules_triggered),
    "score_triggered": bool(score_triggered),
    "z_score": float(z_failed)
}