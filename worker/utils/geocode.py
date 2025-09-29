"""
Geocoding utilities for location extraction
"""
from typing import Tuple, Optional
import re

# Nordic airports
AIRPORTS = {
    # Denmark
    "københavn lufthavn": (55.6180, 12.6476, "Copenhagen Airport"),
    "copenhagen airport": (55.6180, 12.6476, "Copenhagen Airport"),
    "kastrup": (55.6180, 12.6476, "Copenhagen Airport"),
    "aalborg lufthavn": (57.0928, 9.8492, "Aalborg Airport"),
    "aalborg airport": (57.0928, 9.8492, "Aalborg Airport"),
    "billund lufthavn": (55.7403, 9.1518, "Billund Airport"),
    "billund airport": (55.7403, 9.1518, "Billund Airport"),

    # Norway
    "oslo gardermoen": (60.1976, 11.1004, "Oslo Airport"),
    "gardermoen": (60.1976, 11.1004, "Oslo Airport"),
    "bergen lufthavn": (60.2934, 5.2180, "Bergen Airport"),
    "flesland": (60.2934, 5.2180, "Bergen Airport"),

    # Sweden
    "stockholm arlanda": (59.6498, 17.9230, "Stockholm Arlanda"),
    "arlanda": (59.6498, 17.9230, "Stockholm Arlanda"),
    "göteborg landvetter": (57.6628, 12.2798, "Gothenburg Airport"),
    "landvetter": (57.6628, 12.2798, "Gothenburg Airport"),

    # Finland
    "helsinki vantaa": (60.3172, 24.9633, "Helsinki Airport"),
    "helsinki-vantaa": (60.3172, 24.9633, "Helsinki Airport"),
}

# Nordic harbors
HARBORS = {
    # Denmark
    "københavn havn": (55.6900, 12.6000, "Copenhagen Harbor"),
    "copenhagen harbor": (55.6900, 12.6000, "Copenhagen Harbor"),
    "aarhus havn": (56.1500, 10.2270, "Aarhus Harbor"),
    "aalborg havn": (57.0556, 9.9190, "Aalborg Harbor"),
    "esbjerg havn": (55.4650, 8.4450, "Esbjerg Harbor"),

    # Norway
    "oslo havn": (59.9075, 10.7374, "Oslo Harbor"),
    "bergen havn": (60.3990, 5.3200, "Bergen Harbor"),
    "stavanger havn": (58.9700, 5.7330, "Stavanger Harbor"),

    # Sweden
    "stockholm hamn": (59.3293, 18.0686, "Stockholm Harbor"),
    "göteborg hamn": (57.6950, 11.8530, "Gothenburg Harbor"),
    "malmö hamn": (55.6130, 12.9830, "Malmö Harbor"),
}

# Military/Defense sites
MILITARY = {
    "karup": (56.2975, 9.1241, "Karup Air Base"),
    "skrydstrup": (55.2214, 9.2670, "Skrydstrup Air Base"),
    "værløse": (55.7830, 12.3419, "Former Værløse Air Base"),
}

def extract_location(text: str) -> Tuple[Optional[float], Optional[float], Optional[str], Optional[str]]:
    """
    Extract location from text
    Returns: (lat, lon, location_name, asset_type)
    """
    text_lower = text.lower()

    # Check airports first (highest priority)
    for key, (lat, lon, name) in AIRPORTS.items():
        if key in text_lower:
            return lat, lon, name, "airport"

    # Check harbors
    for key, (lat, lon, name) in HARBORS.items():
        if key in text_lower:
            return lat, lon, name, "harbor"

    # Check military sites
    for key, (lat, lon, name) in MILITARY.items():
        if key in text_lower:
            return lat, lon, name, "military"

    # Check for generic location mentions
    if "lufthavn" in text_lower or "airport" in text_lower:
        # Default to Copenhagen if unspecified airport
        return 55.6180, 12.6476, "Unknown Airport", "airport"

    if "havn" in text_lower or "harbor" in text_lower or "port" in text_lower:
        # Default to Copenhagen harbor if unspecified
        return 55.6900, 12.6000, "Unknown Harbor", "harbor"

    # Default to Copenhagen center if no location found
    return 55.6761, 12.5683, None, "other"

def get_country_from_location(lat: float, lon: float) -> str:
    """
    Determine country from coordinates (simplified)
    """
    # Rough bounding boxes
    if 54.5 <= lat <= 57.8 and 8.0 <= lon <= 15.5:
        return "DK"  # Denmark
    elif 57.0 <= lat <= 71.5 and 4.0 <= lon <= 31.5:
        if lon < 13.0:
            return "NO"  # Norway
        else:
            return "SE"  # Sweden
    elif 59.0 <= lat <= 70.5 and 19.0 <= lon <= 32.0:
        return "FI"  # Finland
    else:
        return "DK"  # Default to Denmark