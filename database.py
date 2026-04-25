import sqlite3
import json
from typing import List, Dict

DB_NAME = "creators.db"

def init_db():
    """Initializes the SQLite database with required tables."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Table for creators
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS creators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT,
            channel_id TEXT UNIQUE,
            username TEXT,
            full_name TEXT,
            profile_url TEXT,
            follower_count INTEGER,
            engagement_rate REAL,
            niche TEXT,
            segment TEXT,
            brand_fit_score REAL,
            fit_label TEXT,
            contact_email TEXT,
            outreach_email TEXT,
            collaboration_strategy TEXT,
            data JSON
        )
    """)
    
    # Table for outreach logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS outreach_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            results JSON,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def save_creators(creators: List[Dict]):
    """Saves or updates creators in the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    for c in creators:
        cursor.execute("""
            INSERT OR REPLACE INTO creators (
                platform, channel_id, username, full_name, profile_url, 
                follower_count, engagement_rate, niche, segment, 
                brand_fit_score, fit_label, contact_email, 
                outreach_email, collaboration_strategy, data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            c.get("platform"),
            c.get("channel_id"),
            c.get("username"),
            c.get("full_name") or c.get("channel_title"),
            c.get("profile_url"),
            c.get("subscriber_count", 0) or c.get("follower_count", 0),
            c.get("engagement_rate", 0.0),
            c.get("niche"),
            c.get("segment"),
            c.get("brand_fit_score", 0.0),
            c.get("fit_label"),
            c.get("contact_email"),
            c.get("outreach_email"),
            c.get("collaboration_strategy"),
            json.dumps(c)
        ))
    
    conn.commit()
    conn.close()

def save_outreach_log(outreach_type: str, results: Dict):
    """Logs the results of an outreach campaign."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO outreach_logs (type, results) VALUES (?, ?)",
        (outreach_type, json.dumps(results))
    )
    conn.commit()
    conn.close()
