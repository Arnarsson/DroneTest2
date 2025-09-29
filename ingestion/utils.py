"""
Utility functions for ingestion
"""
import re
import hashlib
from datetime import datetime, timezone
from typing import Optional, Tuple, Dict
import dateutil.parser
from config import DANISH_AIRPORTS, DANISH_HARBORS, CRITICAL_KEYWORDS

def extract_location(text: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """
    Extract location from text by looking for known places
    Returns (lat, lon, asset_type)
    """
    text_lower = text.lower()

    # Check airports first (highest priority)
    for airport, coords in DANISH_AIRPORTS.items():
        if airport in text_lower:
            return coords["lat"], coords["lon"], "airport"

    # Check harbors
    for harbor, coords in DANISH_HARBORS.items():
        if harbor in text_lower:
            return coords["lat"], coords["lon"], "harbor"

    # Check for military/defense mentions
    if any(word in text_lower for word in ["militær", "military", "forsvar", "defense"]):
        # Default to Copenhagen for now
        return 55.6761, 12.5683, "military"

    # Default to Copenhagen center if no specific location found
    return 55.6761, 12.5683, "other"

def extract_datetime(text: str, fallback: datetime = None) -> datetime:
    """
    Extract datetime from text using various formats
    """
    if fallback is None:
        fallback = datetime.now(timezone.utc)

    # Danish date patterns
    patterns = [
        r'(\d{1,2})\.\s*(\w+)\s+(\d{4})\s+kl\.\s*(\d{1,2})[:\.](\d{2})',  # 25. december 2024 kl. 14:30
        r'(\d{1,2})/(\d{1,2})-(\d{4})\s+kl\.\s*(\d{1,2})[:\.](\d{2})',     # 25/12-2024 kl. 14:30
        r'(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2})',                      # 2024-12-25 14:30
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                # Parse the matched datetime
                return dateutil.parser.parse(match.group(0), fuzzy=True)
            except:
                continue

    # Try generic parsing
    try:
        return dateutil.parser.parse(text, fuzzy=True)
    except:
        return fallback

def calculate_evidence_score(source_type: str, has_quote: bool, has_official: bool) -> int:
    """
    Calculate evidence score based on source and content
    """
    if source_type == "police" or source_type == "notam":
        return 4
    elif source_type == "media" and has_official:
        return 3
    elif source_type == "media":
        return 2
    else:
        return 1

def generate_incident_hash(title: str, occurred_at: datetime, lat: float, lon: float) -> str:
    """
    Generate a hash for deduplication
    """
    # Round time to nearest hour and location to 2 decimals
    time_str = occurred_at.strftime("%Y-%m-%d-%H")
    location_str = f"{lat:.2f},{lon:.2f}"
    content = f"{title[:50]}_{time_str}_{location_str}"
    return hashlib.md5(content.encode()).hexdigest()

def extract_quote(text: str) -> Optional[str]:
    """
    Extract relevant quote from article text
    """
    # Look for quotes in Danish/English
    quote_patterns = [
        r'"([^"]{20,200})"',  # Quoted text
        r'»([^»]{20,200})»',  # Danish quotes
        r'siger[:\s]+([^.]{20,200})\.',  # "says: ..."
        r'oplyser[:\s]+([^.]{20,200})\.',  # "informs: ..."
    ]

    for pattern in quote_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()

    # Fallback: return first relevant sentence
    sentences = text.split('.')
    for sentence in sentences:
        if any(word in sentence.lower() for word in ["drone", "dron", "lufthavn"]):
            return sentence.strip()[:200]

    return None

def is_drone_incident(title: str, content: str) -> bool:
    """
    Check if article is actually about drone incidents
    """
    full_text = (title + " " + content).lower()

    # Must contain drone-related keywords
    has_drone = any(word in full_text for word in [
        "drone", "dron", "uav", "uas", "luftfartøj"
    ])

    # Should not be about drone deliveries or commercial use
    is_commercial = any(word in full_text for word in [
        "levering", "delivery", "amazon", "pakke", "package",
        "tilladelse", "permission", "godkendt", "approved"
    ])

    return has_drone and not is_commercial

def clean_html(html_text: str) -> str:
    """
    Remove HTML tags and clean text
    """
    # Remove HTML tags
    clean = re.sub('<.*?>', '', html_text)
    # Remove extra whitespace
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()