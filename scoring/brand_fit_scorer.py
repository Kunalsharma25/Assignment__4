from typing import List, Dict
import torch
from sentence_transformers import util

def compute_fit_score(creator: Dict, brand: Dict) -> Dict:
    """Computes a composite brand-fit score (0.0 to 1.0)."""
    
    # Factor 1: Semantic Similarity (40%)
    from content.signal_extractor import get_model
    model = get_model()
    
    brand_context = f"{brand.get('offering', '')} {brand.get('target_audience', '')}"
    content_text = creator.get("content_signal_text", "") or creator.get("description", "")
    
    if content_text and brand_context:
        content_emb = model.encode(content_text, convert_to_tensor=True)
        brand_emb = model.encode(brand_context, convert_to_tensor=True)
        semantic_score = float(util.cos_sim(content_emb, brand_emb).item())
    else:
        semantic_score = 0.0
        
    # Factor 2: Keyword Overlap (30%)
    brand_keywords = [kw.lower() for kw in brand.get("keywords", [])]
    content_lower = content_text.lower()
    matches = sum(1 for kw in brand_keywords if kw in content_lower)
    keyword_score = min(matches / max(len(brand_keywords), 1), 1.0)
    
    # Factor 3: Engagement Rate Score (35%)
    # Assume 5% is the benchmark for "excellent"
    engagement_score = min(creator.get("engagement_rate", 0) / 5.0, 1.0)
    
    # Composite
    # Weights (Heavily weighted towards Semantic Fit for better relevancy)
    w_semantic = 0.50
    w_keyword = 0.30
    w_engagement = 0.20
    composite = (semantic_score * w_semantic) + (keyword_score * w_keyword) + (engagement_score * w_engagement)
    creator["brand_fit_score"] = round(composite, 3)
    
    # Labeling
    if composite >= 0.70:
        creator["fit_label"] = "High Fit"
    elif composite >= 0.45:
        creator["fit_label"] = "Medium Fit"
    else:
        creator["fit_label"] = "Low Fit"
        
    return creator

def score_all_creators(creators: List[Dict], brand: Dict) -> List[Dict]:
    """Scores and sorts all creators by brand fit."""
    scored = [compute_fit_score(c, brand) for c in creators]
    scored.sort(key=lambda x: x["brand_fit_score"], reverse=True)
    return scored
