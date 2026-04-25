import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time
from typing import Dict, List

def send_email(to_email: str, subject: str, body: str) -> bool:
    """Sends an email via Gmail SMTP."""
    user = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_APP_PASSWORD")
    
    if not user or not password:
        return False
        
    msg = MIMEMultipart()
    msg["From"] = user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(user, password)
            server.sendmail(user, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[Email] Failed to send to {to_email}: {e}")
        return False

def run_email_campaign(creators: List[Dict], brand: Dict, limit: int = 5):
    """Runs a limited email campaign."""
    sent = 0
    results = {"sent": 0, "failed": 0, "skipped": 0}
    
    for creator in creators:
        if sent >= limit:
            break
            
        email = creator.get("contact_email")
        body = creator.get("outreach_email")
        
        if not email or not body:
            results["skipped"] += 1
            continue
            
        subject = f"Collaboration with {brand.get('name')}"
        if send_email(email, subject, body):
            results["sent"] += 1
            sent += 1
            time.sleep(2) # Rate limiting
        else:
            results["failed"] += 1
            
    return results
