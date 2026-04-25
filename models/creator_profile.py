from pydantic import BaseModel, Field
from typing import Optional, List

class CreatorProfile(BaseModel):
    platform: str
    channel_id: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = Field(None, alias="channel_title")
    profile_url: str
    subscriber_count: Optional[int] = 0
    engagement_rate: float = 0.0
    niche: str
    segment: Optional[str] = "General"
    brand_fit_score: float = 0.0
    fit_label: str = "Low Fit"
    contact_email: Optional[str] = None
    outreach_email: Optional[str] = None
    collaboration_strategy: Optional[str] = None
    content_themes: List[str] = []
    content_signal_text: Optional[str] = None

    class Config:
        populate_by_name = True
