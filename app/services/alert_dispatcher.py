import datetime
import json
import os
import smtplib
from email.mime.text import MIMEText

ALERT_LOG_FILE = "alert_log.json"
ALERT_STATE_FILE = "alert_state.json"


def load_json_file(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return default
    return default


def save_json_file(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def load_alerts():
    return load_json_file(ALERT_LOG_FILE, [])


def save_alerts(alerts):
    save_json_file(ALERT_LOG_FILE, alerts)


def load_alert_state():
    """
    Exemplo de estado:
    {
        "FAILED_RATE": "WARNING",
        "DENIED_RATE": "HEALTHY",
        "REVERSED_RATE": "CRITICAL"
    }
    """
    return load_json_file(ALERT_STATE_FILE, {})


def save_alert_state(state):
    save_json_file(ALERT_STATE_FILE, state)


def send_email_alert(alert_payload):
    # CONFIGURAR COM EMAIL DO MANTEDOR DO PROJETO
    sender_email = "seu_email@gmail.com"
    sender_password = "sua_senha_de_app"
    receiver_email = "destinatario@gmail.com"

    event_type = alert_payload.get("event", "ALERT")
    severity = alert_payload.get("severity", "N/A")

    subject = f"[{event_type}] {alert_payload['metric']} - {severity}"
    body = f"""
{event_type}

Metric: {alert_payload['metric']}
Severity: {severity}
Consecutive Minutes: {alert_payload.get('consecutive_minutes', 'N/A')}
Timestamp: {alert_payload['timestamp']}
Message: {alert_payload['message']}
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
    """
    Regras:
    - Se severity mudou para INFO/WARNING/CRITICAL/SEVERE → dispara 1x
    - Se severity continua igual → não dispara de novo
    - Se severity volta para HEALTHY → registra RECOVERY 1x
    """

    alerts = load_alerts()
    state = load_alert_state()

    last_severity = state.get(metric, "HEALTHY")

    # 1) Se voltou para HEALTHY, registra recovery apenas uma vez
    if severity == "HEALTHY":
        if last_severity != "HEALTHY":
            recovery_payload = {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "metric": metric,
                "event": "RECOVERY",
                "previous_severity": last_severity,
                "severity": "HEALTHY",
                "consecutive_minutes": consecutive_minutes,
                "message": f"{metric} recovered and returned to HEALTHY state"
            }

            alerts.append(recovery_payload)
            save_alerts(alerts)

            state[metric] = "HEALTHY"
            save_alert_state(state)

            send_email_alert(recovery_payload)
            print("✅ RECOVERY REGISTERED:", recovery_payload)
            return recovery_payload

        # Já estava healthy, não faz nada
        return None

    # 2) Se a severidade é a mesma da última enviada, evita spam
    if last_severity == severity:
        print(f"🔁 Duplicate alert prevented for {metric} at severity {severity}")
        return None

    # 3) Se severity mudou e não é healthy, dispara alerta
    alert_payload = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "metric": metric,
        "event": "ALERT",
        "severity": severity,
        "consecutive_minutes": consecutive_minutes,
        "message": f"{metric} anomaly persisted for {consecutive_minutes} minutes"
    }

    alerts.append(alert_payload)
    save_alerts(alerts)

    state[metric] = severity
    save_alert_state(state)

    send_email_alert(alert_payload)

    print("🚨 ALERT DISPATCHED:", alert_payload)

    return alert_payload