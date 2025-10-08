"""
Geographic Analyzer with Confidence Scoring
Intelligent analysis of incident geography with context detection
"""
import re
from typing import Optional, Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

# Foreign country/location keywords (WAR ZONES and excluded regions ONLY)
# NOTE: EU countries are INCLUDED in coverage, not foreign!
FOREIGN_KEYWORDS = {
    # Eastern Europe WAR ZONES (highest priority to exclude)
    'ukraina', 'ukraine', 'ukrainsk', 'ukrainian', 'kiev', 'kyiv', 'odesa', 'kharkiv', 'lviv',
    'russia', 'rusland', 'russisk', 'russian', 'moscow', 'moskva', 'st. petersburg',
    'belarus', 'hviderusland', 'hviderussisk', 'belarusian', 'minsk',

    # Middle East
    'israel', 'gaza', 'tel aviv', 'jerusalem',
    'iran', 'tehran', 'syria', 'damascus', 'iraq', 'baghdad',

    # Asia
    'china', 'beijing', 'shanghai', 'japan', 'tokyo', 'korea', 'seoul', 'india', 'delhi', 'mumbai',

    # Africa (if incidents appear)
    'africa', 'cairo', 'johannesburg', 'nairobi',

    # Americas (if incidents appear)
    'united states', 'usa', 'washington', 'new york', 'canada', 'mexico'
}

# European context indicators (suggests European response to foreign events)
EUROPEAN_CONTEXT_KEYWORDS = [
    'denmark responds', 'norwegian authorities', 'swedish defense', 'finnish government',
    'nordic', 'scandinavian', 'nordic countries', 'scandinavian countries',
    'danish foreign minister', 'norwegian prime minister', 'swedish foreign office',
    'meets in copenhagen', 'summit in oslo', 'conference in stockholm',
    'nordic cooperation', 'nordic ministers', 'nordic leaders',
    'denmark comments', 'norway reacts', 'sweden responds', 'finland addresses',
    # EU/European indicators
    'eu responds', 'european union', 'european authorities', 'european defense',
    'nato responds', 'nato allies', 'nato meeting',
    'uk government', 'british authorities', 'german defense', 'french government',
    'european summit', 'eu summit', 'brussels meeting'
]

# European cities/locations (whitelist for confidence boost)
EUROPEAN_CITIES = {
    # Denmark
    'copenhagen', 'københavn', 'aarhus', 'odense', 'aalborg', 'esbjerg', 'roskilde',
    'kastrup', 'billund',

    # Norway
    'oslo', 'bergen', 'trondheim', 'stavanger', 'tromsø', 'drammen', 'kristiansand',
    'bodø', 'gardermoen', 'ålesund',

    # Sweden
    'stockholm', 'göteborg', 'gothenburg', 'malmö', 'uppsala', 'linköping', 'örebro',
    'helsingborg', 'arlanda', 'bromma',

    # Finland
    'helsinki', 'espoo', 'tampere', 'vantaa', 'oulu', 'turku', 'jyväskylä',
    'lahti', 'kuopio', 'vantaa',

    # Iceland
    'reykjavík', 'reykjavik', 'keflavík', 'keflavik', 'akureyri',

    # UK
    'london', 'manchester', 'birmingham', 'edinburgh', 'glasgow', 'liverpool', 'bristol',
    'gatwick', 'heathrow', 'stansted', 'luton', 'belfast', 'cardiff',

    # Germany
    'berlin', 'munich', 'münchen', 'frankfurt', 'hamburg', 'cologne', 'köln', 'düsseldorf',
    'stuttgart', 'dortmund', 'essen', 'leipzig', 'dresden', 'nuremberg',

    # Poland
    'warsaw', 'warszawa', 'krakow', 'kraków', 'gdansk', 'gdańsk', 'wroclaw', 'wrocław',
    'poznan', 'poznań', 'lublin', 'szczecin',

    # France
    'paris', 'lyon', 'marseille', 'toulouse', 'nice', 'nantes', 'strasbourg', 'bordeaux',
    'cdg', 'orly', 'charles de gaulle',

    # Spain
    'madrid', 'barcelona', 'valencia', 'seville', 'sevilla', 'malaga', 'málaga',
    'bilbao', 'palma', 'mallorca',

    # Italy
    'rome', 'roma', 'milan', 'milano', 'naples', 'napoli', 'turin', 'torino',
    'venice', 'venezia', 'florence', 'firenze', 'bologna', 'genoa', 'genova',

    # Belgium
    'brussels', 'bruxelles', 'brussel', 'antwerp', 'antwerpen', 'ghent', 'gent',
    'charleroi', 'liège', 'bruges', 'brugge',

    # Netherlands
    'amsterdam', 'rotterdam', 'the hague', 'den haag', 'utrecht', 'eindhoven',
    'schiphol', 'groningen', 'tilburg',

    # Baltic states
    'tallinn', 'riga', 'vilnius', 'tartu', 'kaunas', 'klaipeda',

    # Ireland
    'dublin', 'cork', 'galway', 'limerick', 'shannon',

    # Portugal
    'lisbon', 'lisboa', 'porto', 'faro', 'madeira',

    # Austria
    'vienna', 'wien', 'salzburg', 'innsbruck', 'graz',

    # Switzerland
    'zurich', 'zürich', 'geneva', 'genève', 'basel', 'bern', 'lausanne'
}


def check_foreign_keywords(text: str) -> List[str]:
    """
    Check text for foreign location keywords

    Returns:
        List of matched foreign keywords
    """
    text_lower = text.lower()
    matches = []

    for keyword in FOREIGN_KEYWORDS:
        # Use word boundaries to avoid false matches
        if re.search(rf'\b{re.escape(keyword)}\b', text_lower):
            matches.append(keyword)

    return matches


def extract_european_cities(text: str) -> List[str]:
    """
    Extract European cities mentioned in text

    Returns:
        List of European cities found
    """
    text_lower = text.lower()
    cities_found = []

    for city in EUROPEAN_CITIES:
        if re.search(rf'\b{re.escape(city)}\b', text_lower):
            cities_found.append(city)

    return cities_found


def has_european_context(content: str) -> bool:
    """
    Check if content suggests European response to foreign events

    Examples:
    - "Denmark responds to Russian drone attacks in Ukraine"
    - "EU ministers meet in Brussels to discuss drone policy"
    - "UK authorities comment on China's drone development"

    Returns:
        True if European context indicators found
    """
    content_lower = content.lower()
    return any(keyword in content_lower for keyword in EUROPEAN_CONTEXT_KEYWORDS)


def analyze_incident_geography(
    title: str,
    content: str,
    lat: Optional[float],
    lon: Optional[float]
) -> Dict[str, any]:
    """
    Smart geographic analysis with confidence scoring and context detection
    Updated for EUROPEAN coverage (not just Nordic)

    Args:
        title: Incident title
        content: Incident content/narrative
        lat: Latitude coordinate
        lon: Longitude coordinate

    Returns:
        {
            'is_nordic': bool - Should incident be ingested? (NOTE: name kept for compatibility, but checks EUROPEAN coverage)
            'confidence': float - Confidence score (0.0-1.0)
            'reason': str - Human-readable explanation
            'flags': List[str] - Concerns and indicators
        }
    """
    flags = []
    confidence = 1.0
    full_text = title + " " + content

    # VALIDATION 1: Coordinates must be in European coverage region
    if lat is None or lon is None:
        return {
            'is_nordic': False,
            'confidence': 0.0,
            'reason': 'No coordinates provided',
            'flags': ['missing_coords']
        }

    # European coverage: 35-71°N, -10-31°E
    # Covers: Nordic + UK + Ireland + Western/Central Europe + Baltics
    in_european_region = (35 <= lat <= 71 and -10 <= lon <= 31)
    if not in_european_region:
        return {
            'is_nordic': False,
            'confidence': 1.0,
            'reason': f'Coordinates outside European coverage region ({lat}, {lon})',
            'flags': ['coords_outside_europe']
        }

    flags.append('coords_in_europe')

    # VALIDATION 2: Check for excluded location keywords (war zones, non-EU)
    foreign_matches = check_foreign_keywords(full_text)

    if foreign_matches:
        # Check if it's a European response TO foreign events
        if has_european_context(content):
            confidence -= 0.4  # Uncertain - might be European article about foreign events
            flags.append('foreign_mentioned_with_european_context')
            flags.append(f'foreign_keywords: {", ".join(foreign_matches[:3])}')

            reason = f'Uncertain: Foreign keywords ({", ".join(foreign_matches[:3])}) with European context'
        else:
            # Clear foreign incident (war zone, Asia, etc.)
            return {
                'is_nordic': False,
                'confidence': 1.0,
                'reason': f'Excluded region incident: {", ".join(foreign_matches[:3])}',
                'flags': ['foreign_incident'] + [f'keyword:{k}' for k in foreign_matches[:3]]
            }

    # VALIDATION 3: European location verification (whitelist approach)
    european_cities = extract_european_cities(full_text)
    if european_cities:
        confidence = min(1.0, confidence + 0.2)
        flags.append(f'european_cities: {", ".join(european_cities[:3])}')

    # VALIDATION 4: Check for official sources (confidence boost)
    if any(word in content.lower() for word in ['politi', 'police', 'forsvar', 'defense', 'myndighed', 'authority']):
        confidence = min(1.0, confidence + 0.1)
        flags.append('official_source')

    # Determine if incident should be ingested
    is_european = confidence >= 0.5

    if is_european:
        reason = 'Passed all checks - European incident confirmed'
    else:
        reason = f'Low confidence ({confidence:.2f}) - Excluded region content likely'

    return {
        'is_nordic': is_european,  # NOTE: Key name kept for backwards compatibility
        'confidence': round(confidence, 2),
        'reason': reason,
        'flags': flags
    }


def is_nordic_incident(title: str, content: str, lat: Optional[float], lon: Optional[float]) -> bool:
    """
    Legacy compatibility wrapper for existing code

    Calls analyze_incident_geography() and returns simple boolean
    """
    analysis = analyze_incident_geography(title, content, lat, lon)

    if not analysis['is_nordic']:
        logger.info(f"⏭️  Blocked: {title[:60]}...")
        logger.info(f"   Reason: {analysis['reason']}")
        logger.info(f"   Confidence: {analysis['confidence']}")

    return analysis['is_nordic']


# For backwards compatibility, keep the old function available
__all__ = ['analyze_incident_geography', 'is_nordic_incident']
