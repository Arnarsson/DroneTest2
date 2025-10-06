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
    Returns (lat, lon, asset_type) or (None, None, None) if location cannot be determined

    NOTE: We return None instead of default coordinates to avoid clustering
    unrelated incidents at the same fallback location.
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

    # Check for military/defense mentions with specific locations
    # TODO: Add more specific military base coordinates
    # For now, skip incidents without specific location mentions

    # Return None if no specific location found
    # This prevents clustering unrelated incidents at a default coordinate
    return None, None, None

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

def calculate_evidence_score(trust_weight: int, has_official: bool = False) -> int:
    """
    Calculate evidence score based on source trust weight and official quotes

    Args:
        trust_weight: Source trust level (1-4)
        has_official: Whether content contains official quotes

    Returns:
        Evidence score (1-4):
        - 4: Official sources (trust_weight=4)
        - 3: Credible source (trust_weight=3) with official quote
        - 2: Credible source (trust_weight>=2)
        - 1: Low trust source (trust_weight=1)
    """
    if trust_weight == 4:
        return 4
    elif trust_weight == 3 and has_official:
        return 3
    elif trust_weight >= 2:
        return 2
    else:
        return 1

def generate_incident_hash(title: str, occurred_at: datetime, lat: float, lon: float) -> str:
    """
    Generate a hash for deduplication based on location and time window.

    IMPORTANT: Title is NOT used in hash generation because:
    - Different news outlets report the same event with different headlines
    - Same incident gets multiple articles with different titles
    - We want ONE incident with MULTIPLE sources, not multiple incidents

    Deduplication strategy:
    - Location rounded to 0.01° (≈1.1km radius)
    - Time rounded to 6-hour window
    - Same location+time = Same incident → Add as source
    """
    # Round time to 6-hour window (00, 06, 12, 18)
    # This groups articles about events happening in the same general timeframe
    hour_window = (occurred_at.hour // 6) * 6
    time_str = f"{occurred_at.strftime('%Y-%m-%d')}-{hour_window:02d}"

    # Round location to ~1km precision (0.01 degrees)
    location_str = f"{lat:.2f},{lon:.2f}"

    # Hash based ONLY on location + time (NOT title)
    content = f"{time_str}_{location_str}"
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

def is_nordic_incident(title: str, content: str, lat: Optional[float], lon: Optional[float]) -> bool:
    """
    Check if incident occurred in Nordic region (not just covered by Nordic news).

    This prevents ingesting foreign incidents (e.g., Ukrainian drone attacks) that are
    merely reported by Nordic news sources but didn't occur in the Nordic region.

    Returns True if:
    - Coordinates are in Nordic region AND text doesn't mention foreign locations
    - No coordinates but text doesn't mention non-Nordic locations

    Returns False if:
    - Coordinates outside Nordic region, OR
    - Text mentions foreign locations (even if coords are Nordic - e.g., context mentions)
    """
    full_text = (title + " " + content).lower()

    # Check text for foreign location mentions FIRST (applies to all incidents)
    # This catches cases where Nordic coords are extracted from context mentions

    # Non-Nordic country/location keywords
    foreign_locations = [
        # Eastern Europe (including adjective forms in Nordic languages)
        "ukraina", "ukraine", "ukrainsk", "ukrainian", "kiev", "kyiv", "odesa", "kharkiv", "lviv",
        "russia", "rusland", "russisk", "russian", "moscow", "moskva", "st. petersburg",
        "belarus", "hviderusland", "hviderussisk", "belarusian", "minsk",
        "poland", "polen", "polsk", "polish", "warsaw", "warszawa", "krakow",

        # Central/Western Europe (non-Nordic, including adjective forms)
        "germany", "tyskland", "tysk", "german", "berlin", "münchen", "munich", "hamburg", "frankfurt",
        "france", "frankrig", "fransk", "french", "paris", "lyon", "marseille",
        "netherlands", "holland", "nederlandsk", "dutch", "amsterdam", "rotterdam",
        "belgium", "belgien", "belgisk", "belgian", "brussels", "bruxelles",
        "uk", "england", "britain", "britisk", "british", "london", "manchester",
        "spain", "spanien", "spansk", "spanish", "madrid", "barcelona",
        "italy", "italien", "italiensk", "italian", "rome", "milano", "milan",

        # Baltic states (included in detection as non-Nordic, with adjective forms)
        "estonia", "estland", "estisk", "estonian", "tallinn",
        "latvia", "letland", "lettisk", "latvian", "riga",
        "lithuania", "litauen", "litauisk", "lithuanian", "vilnius",

        # Middle East
        "israel", "gaza", "tel aviv", "jerusalem",
        "iran", "tehran",
        "syria", "damascus",
        "iraq", "baghdad",

        # Asia
        "china", "beijing", "shanghai",
        "japan", "tokyo",
        "korea", "seoul",
        "india", "delhi", "mumbai"
    ]

    # Check if any foreign location is mentioned
    # Use word boundaries to avoid false matches
    for location in foreign_locations:
        if re.search(rf'\b{re.escape(location)}\b', full_text):
            return False

    # No foreign locations in text - now check coordinates if available
    if lat is not None and lon is not None:
        # Nordic region: roughly 54-71°N, 4-31°E
        if 54 <= lat <= 71 and 4 <= lon <= 31:
            return True
        else:
            # Coordinates outside Nordic region
            return False

    # No foreign locations in text and no coordinates - assume Nordic
    return True

def is_drone_incident(title: str, content: str) -> bool:
    """
    Check if article is actually about drone incidents
    Uses word boundary matching to avoid false positives (e.g., "dronning" = queen)
    """
    full_text = (title + " " + content).lower()

    # Must contain drone-related keywords (word boundary to avoid "dronning"/queen false positive)
    has_drone = any(re.search(rf'\b{re.escape(word)}\b', full_text) for word in [
        "drone", "dron", "uav", "uas", "luftfartøj"
    ])

    # Must contain incident indicators (not just mentions of drones)
    # Require ACTUAL observation, action, or response to an incident
    has_observation = any(word in full_text for word in [
        "observed", "spotted", "sighted", "set", "opdaget", "filmed", "recorded",
        "detected", "detekteret", "mistænk", "suspect"
    ])

    has_action = any(word in full_text for word in [
        "closed", "closure", "lukket", "lukning",
        "diverted", "omdirigeret",
        "suspended", "suspenderet", "grounded",
        "evacuated", "evacuated"
    ])

    has_response = any(word in full_text for word in [
        "investigating", "undersøger", "investigation", "undersøgelse",
        "searching", "søger", "responding", "reagerer",
        "politi", "police", "authorities", "myndigheder"
    ])

    has_incident = has_observation or has_action or has_response

    # Should not be about drone deliveries, commercial use, or royalty
    is_excluded = any(word in full_text for word in [
        "levering", "delivery", "amazon", "pakke", "package",
        "tilladelse", "permission", "godkendt", "approved",
        "dronning", "kronprins", "royal", "kongelig",  # Exclude royalty articles
        "bryllup", "wedding", "parforhold", "relationship"  # Exclude personal news
    ])

    # CRITICAL: Exclude non-Nordic international incidents
    # These are often reported by Nordic news but happened elsewhere
    is_international = any(location in full_text for location in [
        "ukraina", "ukraine", "kiev", "kyiv", "odesa",  # Ukraine
        "russia", "rusland", "moscow", "moskva",  # Russia
        "münchen", "munich", "berlin", "germany", "tyskland",  # Germany
        "poland", "polen", "warsaw", "warszawa",  # Poland (unless Nordic-specific)
        "middle east", "mellemøsten", "israel", "gaza",  # Middle East
        "china", "kina", "beijing",  # China
        "united states", "usa", "washington", "new york"  # USA
    ])

    # Exclude policy/announcement articles (not actual incidents)
    is_policy = any(phrase in full_text for phrase in [
        "announced", "announcement", "annonceret",
        "proposed", "proposal", "forslag",
        "will be called", "vil blive kaldt",
        "plans to", "planer om",
        "vows to", "lover at",
        "development of", "udvikling af",
        "jump-started", "iværksat",
        "proposed measures", "foreslåede foranstaltninger",
        "eastern flank watch",
        "drone wall",  # Specific to policy articles about drone defense systems
        # NEW: Enhanced patterns for policy/announcement detection
        "drone ban", "droneforbud", "forbud",
        "new regulation", "ny regulering", "nye regler",
        "will impose", "vil indføre",
        "in connection with", "i forbindelse med",  # catches "i forbindelse med EU-formandskab"
        "eu-formandskab", "eu presidency", "summit",
        "giver nyt", "giver nye",  # "gives new" (ban/regulation)
        "kommer til byen"  # "coming to the city" (officials/ministers)
    ])

    # Exclude defense/security deployment articles (not actual incidents)
    is_defense = any(phrase in full_text for phrase in [
        "rushed to", "sent to", "deployed to",
        "defend against", "forsvare mod", "forsvare imod",
        "military assets", "militære aktiver",
        "frigate", "fregat", "troops", "tropper", "styrker",
        "radars", "radar", "increased security",
        "bolster defense", "styrke forsvar", "øge sikkerheden",
        "navy ship", "naval vessel", "warship",
        "military equipment", "militært udstyr"
    ])

    return has_drone and has_incident and not is_excluded and not is_policy and not is_international and not is_defense

def clean_html(html_text: str) -> str:
    """
    Remove HTML tags and clean text
    """
    # Remove HTML tags
    clean = re.sub('<.*?>', '', html_text)
    # Remove extra whitespace
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()