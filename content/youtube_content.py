from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
import os
from typing import List, Dict

def get_latest_video_id(channel_id: str) -> str:
    """Fetches the latest video ID for a given channel."""
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        return None
    
    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        response = youtube.search().list(
            channelId=channel_id,
            part="id",
            order="date",
            maxResults=1,
            type="video"
        ).execute()
        
        items = response.get("items", [])
        return items[0]["id"]["videoId"] if items else None
    except Exception as e:
        print(f"[Content] Error fetching latest video for {channel_id}: {e}")
        return None

def get_transcript(video_id: str) -> str:
    """Fetches the transcript for a video ID."""
    if not video_id:
        return ""
    
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(
            video_id, 
            languages=["hi", "en", "en-IN"]
        )
        return " ".join([t["text"] for t in transcript_list])
    except Exception:
        # Many videos don't have transcripts; this is a common case
        return ""

def analyze_creator_content(creator: Dict) -> Dict:
    """Fetches transcript and video title for content analysis."""
    channel_id = creator.get("channel_id")
    video_id = creator.get("sample_video_id") or get_latest_video_id(channel_id)
    
    if video_id:
        transcript = get_transcript(video_id)
        creator["transcript_text"] = transcript
    else:
        creator["transcript_text"] = ""
        
    return creator
