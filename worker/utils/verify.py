"""
Verification utilities to ensure quality and prevent hallucinations
"""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict
from urllib.parse import urlparse
import re

class ExtractedIncident(BaseModel):
    """Structured extraction result with evidence"""
    is_incident: bool = False
    title: Optional[str] = None
    location_name: Optional[str] = None
    occurred_at_iso: Optional[str] = None
    narrative: Optional[str] = None
    confirmations: List[str] = Field(default_factory=list)  # ["police", "notam", "airport"]
    quotes: Dict[str, str] = Field(default_factory=dict)    # field -> exact supporting quote

def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    try:
        d = urlparse(url).netloc.lower()
        return d.split(":")[0].replace("www.", "")
    except Exception:
        return ""

def score_from_source(src_domain: str, declared_type: Optional[str], trusted: set) -> int:
    """Calculate evidence score based on source"""
    if declared_type in {"police", "notam"}:
        return 4
    if src_domain in trusted:
        return 3
    if declared_type == "media":
        return 2
    return 1

def require_quotes(incident: ExtractedIncident) -> bool:
    """Check if incident has required supporting quotes"""
    # Require at least one quote for key fields
    has_quote = any(
        incident.quotes.get(k)
        for k in ("title", "location_name", "confirmations", "narrative")
    )
    return has_quote

def safe_accept(incident: ExtractedIncident, evidence_score: int) -> bool:
    """Determine if incident should be auto-accepted"""
    # Only accept when:
    # 1. Identified as incident
    # 2. Has minimum evidence score
    # 3. Has supporting quotes (no hallucinations)
    return (
        incident.is_incident and
        evidence_score >= 2 and
        require_quotes(incident)
    )

def is_drone_related(text: str) -> bool:
    """Check if text contains drone-related keywords"""
    keywords = [
        "drone", "dron", "uav", "uas",
        "unmanned aerial", "ubemannede luftfartøj",
        "quadcopter", "multirotor"
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)

def extract_police_quote(text: str) -> Optional[str]:
    """Extract police statement from text"""
    # Danish patterns
    patterns = [
        r'"([^"]{20,300})"',  # Quoted text
        r'»([^»]{20,300})»',  # Danish quotes
        r'(?:politiet|police|myndighed)(?:\s+\w+){0,3}:\s*([^.]{20,300})',
        r'(?:siger|oplyser|meddeler|fortæller)[:\s]+([^.]{20,300})',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None

def validate_coordinates(lat: float, lon: float) -> bool:
    """Validate coordinate ranges"""
    return -90 <= lat <= 90 and -180 <= lon <= 180