from typing import List, Dict

INDIA_INDICATORS = [
    "india", "bharat", "mumbai", "delhi", "bangalore", "bengaluru",
    "hyderabad", "chennai", "kolkata", "pune", "ahmedabad", "jaipur",
    "₹", "inr", "rupee", "hindi", "marathi", "tamil", "telugu", "kannada"
]

def is_india_based(creator: Dict) -> bool:
    """Check if creator is India-based using country code or text indicators."""
    if creator.get("country") == "IN":
        return True
    
    text = (
        creator.get("description", "") +
        creator.get("channel_title", "") +
        creator.get("sample_video_title", "")
    ).lower()
    return any(indicator in text for indicator in INDIA_INDICATORS)

def is_micro_influencer(creator: Dict, min_subs=5000, max_subs=100000) -> bool:
    """Checks if the subscriber count falls within the micro-influencer range."""
    count = creator.get("subscriber_count", 0)
    return min_subs <= count <= max_subs

def is_keyword_relevant(creator: Dict, keywords: List[str]) -> bool:
    """Checks if the creator's metadata contains at least one word from the keywords."""
    text = (
        creator.get("description", "") +
        creator.get("channel_title", "") +
        creator.get("sample_video_title", "")
    ).lower()
    
    # Split keywords into individual words for broader matching
    all_kw_words = set()
    for kw in keywords:
        for word in kw.lower().split():
            if len(word) > 3: # Ignore short words like "in", "a", "the"
                all_kw_words.add(word)
                
    return any(word in text for word in all_kw_words)

def apply_filters(creators: List[Dict], keywords: List[str]) -> List[Dict]:
    """Applies all filters and logs dropout reasons."""
    filtered = []
    dropped = {"subs": 0, "region": 0, "relevance": 0}
    print(f"[Filter] Processing {len(creators)} raw creators...")
    
    for c in creators:
        if not is_micro_influencer(c):
            dropped["subs"] += 1
            continue
        if not is_india_based(c):
            dropped["region"] += 1
            continue
        if not is_keyword_relevant(c, keywords):
            dropped["relevance"] += 1
            continue
        filtered.append(c)
    
    print(f"[Filter] Dropout reasons: {dropped}")
    print(f"[Filter] {len(creators)} -> {len(filtered)} creators after filtering")
    return filtered
