import datetime
import json
import os
import smtplib
from email.mime.text import MIMEText

ALERT_LOG_FILE = "alert_log.json"


def load_alerts():
    if os.path.exists(ALERT_LOG_FILE):
        with open(ALERT_LOG_FILE, "r") as f:
            return json.load(f)
    return []


def save_alerts(alerts):
    with open(ALERT_LOG_FILE, "w") as f:
        json.dump(alerts, f, indent=4)

def send_email_alert(alert_payload):

    # CONFIGURAR COM SEU EMAIL
    sender_email = "seu_email@gmail.com"
    sender_password = "sua_senha_de_app"
    receiver_email = "destinatario@gmail.com"

    subject = f"[ALERT] {alert_payload['metric']} - {alert_payload['severity']}"
    body = f"""
    ALERT TRIGGERED

    Metric: {alert_payload['metric']}
    Severity: {alert_payload['severity']}
    Consecutive Minutes: {alert_payload['consecutive_minutes']}
    Timestamp: {alert_payload['timestamp']}
    """

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()

        print("📧 Email alert sent")

    except Exception as e:
        print("Email error:", str(e))


def dispatch_alert(metric, severity, consecutive_minutes):

    if severity == "HEALTHY":
        return None  # nunca gera alerta healthy

    alerts = load_alerts()

    # Verifica último alerta da mesma métrica
    last_alert = None
    for alert in reversed(alerts):
        if alert["metric"] == metric:
            last_alert = alert
            break

    # Anti-spam:
    # Só dispara se severidade mudou
    if last_alert and last_alert["severity"] == severity:
        print(f"🔁 Duplicate alert prevented for {metric}")
        return None

    alert_payload = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "metric": metric,
        "severity": severity,
        "consecutive_minutes": consecutive_minutes,
        "message": f"{metric} anomaly persisted for {consecutive_minutes} minutes"
    }

    alerts.append(alert_payload)
    save_alerts(alerts)
    send_email_alert(alert_payload)

    print("🚨 ALERT DISPATCHED:", alert_payload)

    return alert_payload