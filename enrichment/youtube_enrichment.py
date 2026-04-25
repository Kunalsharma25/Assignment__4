import re
from typing import Dict

def extract_email(text: str) -> str:
    """Extracts the first email address found in the text."""
    if not text:
        return None
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else None

def classify_niche(text: str) -> str:
    """Performs a simple rule-based niche classification."""
    text_lower = text.lower()
    niche_keywords = {
        "beauty": ["skincare", "makeup", "beauty", "dermatologist", "cosmetics"],
        "education": ["olympiad", "exam", "study", "cbse", "aptitude", "learning"],
        "finance": ["investing", "stocks", "mutual fund", "sip", "budget", "money"],
        "lifestyle": ["vlog", "daily", "travel", "food", "lifestyle"],
    }
    for niche, terms in niche_keywords.items():
        if any(term in text_lower for term in terms):
            return niche
    return "general"

def enrich_youtube_creator(creator: Dict, youtube=None) -> Dict:
    """Enriches a YouTube creator profile with email, niche data, and consistency checks."""
    description = creator.get("description", "")
    
    # 1. Extract email
    creator["contact_email"] = extract_email(description)
    
    # 2. Consistency Check (Analyze last 5 video titles)
    recent_titles = []
    if youtube and creator.get("channel_id"):
        from discovery.youtube_discovery import fetch_recent_video_titles
        recent_titles = fetch_recent_video_titles(youtube, creator["channel_id"])
    
    # Combine everything into a "Channel Signature" for the AI
    channel_signature = (
        description + " " + 
        creator.get("sample_video_title", "") + " " + 
        " ".join(recent_titles)
    )
    
    creator["niche"] = classify_niche(channel_signature)
    # Store signature for the Signal Extractor later
    creator["content_signature"] = channel_signature
    
    # 3. View-Weighted Engagement Score (Optimized Reliability Logic)
    views = creator.get("video_views", 0)
    likes = creator.get("video_likes", 0)
    comments = creator.get("video_comments", 0)
    
    if views <= 0:
        creator["engagement_rate"] = 0.0
        return creator

    # Calculate raw engagement relative to VIEWS
    raw_engagement = ((likes + (2 * comments)) / views) * 100
    
    # Reliability factor (penalizes creators with < 5000 views)
    reliability_factor = min(views / 5000, 1.0)
    
    # Final engagement score
    engagement_score = raw_engagement * reliability_factor
    
    # Cap at 25.0 (Industry standard for realistic outliers)
    creator["engagement_rate"] = round(min(engagement_score, 25.0), 2)
        
    return creator
