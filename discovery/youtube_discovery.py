import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def get_youtube_service():
    """Initializes the YouTube API service."""
    if not YOUTUBE_API_KEY or "YOUR_YOUTUBE_API_KEY" in YOUTUBE_API_KEY:
        return None
    try:
        return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    except Exception as e:
        print(f"[YouTube Discovery] Error initializing service: {e}")
        return None

def search_youtube_creators(keywords: List[str], max_results_per_kw: int = 50) -> List[Dict]:
    """Searches YouTube for channels matching keywords."""
    youtube = get_youtube_service()
    if not youtube:
        print("[YouTube Discovery] Warning: No valid API key found. Skipping search.")
        return []

    discovered = {}
    for keyword in keywords:
        print(f"[YouTube Discovery] Searching for keyword: '{keyword}'")
        try:
            search_response = youtube.search().list(
                q=keyword,
                part="snippet",
                type="video",
                regionCode="IN",
                relevanceLanguage="hi",
                maxResults=max_results_per_kw,
                order="relevance"
            ).execute()

            for item in search_response.get("items", []):
                channel_id = item["snippet"]["channelId"]
                if channel_id not in discovered:
                    discovered[channel_id] = {
                        "platform": "youtube",
                        "channel_id": channel_id,
                        "channel_title": item["snippet"]["channelTitle"],
                        "discovery_keyword": keyword,
                        "sample_video_id": item["id"]["videoId"],
                        "sample_video_title": item["snippet"]["title"],
                    }
        except HttpError as e:
            print(f"[YouTube Discovery] API error for keyword '{keyword}': {e}")
            continue

    return list(discovered.values())

def fetch_channel_stats(channel_ids: List[str]) -> Dict[str, Dict]:
    """Batch-fetches channel statistics."""
    youtube = get_youtube_service()
    if not youtube or not channel_ids:
        return {}

    stats = {}
    for i in range(0, len(channel_ids), 50):
        chunk = channel_ids[i:i+50]
        try:
            response = youtube.channels().list(
                part="statistics,snippet",
                id=",".join(chunk)
            ).execute()

            for item in response.get("items", []):
                cid = item["id"]
                stats[cid] = {
                    "subscriber_count": int(item["statistics"].get("subscriberCount", 0)),
                    "view_count": int(item["statistics"].get("viewCount", 0)),
                    "description": item["snippet"].get("description", ""),
                    "profile_url": f"https://youtube.com/@{item['snippet'].get('customUrl', '').replace('@', '')}",
                }
        except Exception as e:
            print(f"[YouTube Discovery] Error fetching channel stats: {e}")
            continue
    return stats

def fetch_video_stats(video_ids: List[str]) -> Dict[str, Dict]:
    """Batch-fetches video statistics."""
    youtube = get_youtube_service()
    if not youtube or not video_ids:
        return {}

    stats = {}
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i+50]
        try:
            response = youtube.videos().list(
                part="statistics",
                id=",".join(chunk)
            ).execute()

            for item in response.get("items", []):
                vid = item["id"]
                vstats = item["statistics"]
                stats[vid] = {
                    "video_likes": int(vstats.get("likeCount", 0)),
                    "video_comments": int(vstats.get("commentCount", 0)),
                    "video_views": int(vstats.get("viewCount", 0)),
                }
        except Exception as e:
            print(f"[YouTube Discovery] Error fetching video stats: {e}")
            continue
    return stats

def fetch_recent_video_titles(youtube, channel_id, max_results=5):
    """Fetches titles of the latest videos for consistency checks."""
    try:
        channel_res = youtube.channels().list(id=channel_id, part="contentDetails").execute()
        if not channel_res.get("items"):
            return []
        
        uploads_id = channel_res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        playlist_res = youtube.playlistItems().list(
            playlistId=uploads_id, part="snippet", maxResults=max_results
        ).execute()
        
        return [item["snippet"]["title"] for item in playlist_res.get("items", [])]
    except Exception:
        return []

if __name__ == "__main__":
    print("YouTube Discovery Module Ready.")
