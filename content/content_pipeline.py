from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict
from .youtube_content import analyze_creator_content
from .signal_extractor import extract_signals

def process_single_creator(creator: Dict, industry: str) -> Dict:
    """Analyzes content and signals for a single creator."""
    try:
        # 1. Fetch transcript
        creator = analyze_creator_content(creator)
        
        # 2. Extract semantic signals
        full_text = (
            creator.get("description", "") + " " + 
            creator.get("transcript_text", "") + " " + 
            creator.get("content_signature", "")
        )
        signal_results = extract_signals(full_text, industry)
        
        creator["content_signals"] = signal_results["signals"]
        creator["content_signal_score"] = signal_results["signal_score"]
        creator["content_signal_text"] = signal_results["signal_text"]
        creator["content_themes"] = signal_results["signals"][:5]
        
    except Exception as e:
        print(f"[Content Pipeline] Error processing {creator.get('channel_title')}: {e}")
        
    return creator

def run_content_pipeline(creators: List[Dict], industry: str, max_workers: int = 5) -> List[Dict]:
    """Runs content analysis for all creators in parallel."""
    print(f"[Content Pipeline] Analyzing {len(creators)} creators in parallel (workers={max_workers})...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(lambda c: process_single_creator(c, industry), creators))
        
    return results
