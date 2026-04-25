from typing import List, Dict

COLLABORATION_MAP = {
    "beauty": {
        "Skincare Educators": "Product Trial + Review Partnership",
        "Makeup Tutorial Creators": "Paid Sponsorship + Tutorial Integration",
        "Product Review Creators": "Affiliate Partnership (CPA)",
    },
    "education": {
        "Olympiad Prep": "Assessment Ecosystem Partnership",
        "Reasoning & Aptitude": "Workshop & Study Material Collaboration",
        "Student Competition Awareness": "Event Sponsorship",
    },
}

def assign_strategy(creators: List[Dict], industry: str) -> List[Dict]:
    """Assigns a collaboration strategy based on segment and industry."""
    industry_map = COLLABORATION_MAP.get(industry.lower(), {})
    
    for creator in creators:
        segment = creator.get("segment", "General")
        
        if segment in industry_map:
            creator["collaboration_strategy"] = industry_map[segment]
        elif "Specialist" in segment:
            # Dynamic fallback based on segment name
            creator["collaboration_strategy"] = "Targeted Product Review + Barter"
        else:
            creator["collaboration_strategy"] = "Affiliate Partnership (CPA)"
            
    return creators
