import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config

def send_alert(status, score, cycle, machine_name="Engine 1"):
    """
    Sends an email alert when warning or critical threshold is crossed.
    """

    # Email configuration
    SENDER = "watchdogalerts58@gmail.com"
    RECEIVER = "aaaaaliarif@gmail.com"  
    APP_PASSWORD = "lnce fhsw yqah pgqc"  

    # Build subject based on status
    if status == "CRITICAL":
        subject = f"🚨 CRITICAL ALERT — {machine_name} requires immediate attention"
    elif status == "WARNING":
        subject = f"⚠️ WARNING — {machine_name} degradation detected"
    else:
        subject = f"✅ STATUS UPDATE — {machine_name} operating normally"

    # Build email body
    body = f"""
WatchDog Predictive Maintenance Alert
======================================

Machine:        {machine_name}
Status:         {status}
Health Score:   {score}/100
Cycle:          {cycle}
Threshold:      Warning at {config.WARNING_THRESHOLD}, Critical at {config.CRITICAL_THRESHOLD}

Message:
"""

    if status == "CRITICAL":
        body += "IMMEDIATE ACTION REQUIRED. Equipment has entered the critical failure zone. Schedule emergency maintenance now."
    elif status == "WARNING":
        body += "Equipment degradation detected. Health score has crossed the warning threshold. Schedule maintenance soon to prevent failure."
    else:
        body += "Equipment is operating within normal parameters. No action required."

    body += f"""

--------------------------------------
This alert was generated automatically by WatchDog v{config.VERSION}
Do not reply to this email.
"""

    # Build and send the email
    msg = MIMEMultipart()
    msg['From'] = SENDER
    msg['To'] = RECEIVER
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Alert email sent successfully to {RECEIVER}")
        return True
    except Exception as e:
        print(f"Failed to send alert email: {e}")
        return False