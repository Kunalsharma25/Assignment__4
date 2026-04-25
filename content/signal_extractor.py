from sentence_transformers import SentenceTransformer, util
import torch
from typing import List, Dict

# Global model cache for speed
import threading

_model_cache = None
_model_lock = threading.Lock()

def get_model():
    global _model_cache
    with _model_lock:
        if _model_cache is None:
            print("[Content] Loading sentence-transformer model (all-MiniLM-L6-v2) on CPU...")
            _model_cache = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
    return _model_cache

CONTENT_SIGNALS = {
    "beauty": [
        "skincare routine", "moisturizer", "dermatologist", "affordable skincare", 
        "makeup tutorial", "serum", "night routine", "acne treatment"
    ],
    "education": [
        "olympiad", "competitive exam", "reasoning", "math shortcuts", 
        "CBSE", "student tips", "exam strategy", "aptitude"
    ],
    "finance": [
        "SIP", "mutual fund", "investing", "budgeting", 
        "stock market", "emergency fund", "tax saving", "loan"
    ],
    "gaming": ["gameplay", "walkthrough", "stream", "gaming setup", "pc build", "esports", "console", "ps5", "xbox", "gaming chair", "ergonomics"],
    "tech": ["review", "unboxing", "gadgets", "technology", "software", "hardware", "setup tour", "desk setup", "tech nerd", "coding", "productivity"],
    "lifestyle": [
        "daily routine", "productivity", "healthy eating", "travel budget India", "fitness"
    ]
}

def extract_signals(content_text: str, industry: str) -> Dict:
    """Calculates semantic similarity between content and predefined signals."""
    if not content_text or not content_text.strip():
        return {"signals": [], "signal_score": 0.0, "signal_text": ""}

    model = get_model()
    signals = CONTENT_SIGNALS.get(industry, [])
    
    if not signals:
        return {"signals": [], "signal_score": 0.0, "signal_text": content_text[:200]}

    # Encode content and signals
    content_emb = model.encode(content_text, convert_to_tensor=True)
    signal_embs = model.encode(signals, convert_to_tensor=True)
    
    # Calculate cosine similarity
    cosine_scores = util.cos_sim(content_emb, signal_embs)[0]
    
    matched_signals = []
    for i, score in enumerate(cosine_scores):
        if score > 0.45: # Higher threshold for better precision
            matched_signals.append(signals[i])
            
    signal_score = len(matched_signals) / len(signals) if signals else 0
    signal_text = "; ".join(matched_signals) if matched_signals else content_text[:200]
    
    return {
        "signals": matched_signals,
        "signal_score": round(float(signal_score), 3),
        "signal_text": signal_text
    }
