from typing import List, Dict
from .youtube_discovery import search_youtube_creators, fetch_channel_stats, fetch_video_stats

def run_discovery(config: Dict) -> List[Dict]:
    """Runs the full discovery pipeline for all configured keywords."""
    keywords = config.get("keywords", [])
    if not keywords:
        print("[Discovery] No keywords configured. Skipping.")
        return []

    print(f"[Discovery] Starting YouTube discovery for {len(keywords)} keywords...")
    
    # 1. Search for channels
    raw_yt_creators = search_youtube_creators(keywords)
    
    # 2. Fetch stats for those channels and their sample videos
    channel_ids = [c["channel_id"] for c in raw_yt_creators]
    video_ids = [c["sample_video_id"] for c in raw_yt_creators]
    
    yt_stats = fetch_channel_stats(channel_ids)
    video_stats = fetch_video_stats(video_ids)

    # 3. Combine search data with stats
    all_creators = []
    for creator in raw_yt_creators:
        cid = creator["channel_id"]
        vid = creator["sample_video_id"]
        
        if cid in yt_stats:
            creator.update(yt_stats[cid])
            if vid in video_stats:
                creator.update(video_stats[vid])
            all_creators.append(creator)

    print(f"[Discovery] Found {len(all_creators)} creators with full stats.")
    return all_creators
