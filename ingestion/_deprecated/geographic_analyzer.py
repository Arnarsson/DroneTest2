"""
Geographic Analyzer with Confidence Scoring
Intelligent analysis of incident geography with context detection
"""
import re
from typing import Optional, Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

# Foreign country/location keywords (NON-EUROPEAN regions only)
# European coverage: Nordic + UK + Germany + France + Spain + Italy + Poland + Benelux + Baltics
FOREIGN_KEYWORDS = {
    # War zones (Eastern Europe)
    'ukraina', 'ukraine', 'ukrainsk', 'ukrainian', 'kiev', 'kyiv', 'odesa', 'kharkiv', 'lviv',
    'russia', 'rusland', 'russisk', 'russian', 'moscow', 'moskva', 'st. petersburg',
    'belarus', 'hviderusland', 'hviderussisk', 'belarusian', 'minsk',

    # Middle East
    'israel', 'gaza', 'tel aviv', 'jerusalem',
    'iran', 'tehran', 'syria', 'damascus', 'iraq', 'baghdad',
    'saudi arabia', 'yemen', 'lebanon', 'beirut',

    # Asia
    'china', 'beijing', 'shanghai', 'japan', 'tokyo', 'korea', 'seoul', 'india', 'delhi', 'mumbai',
    'pakistan', 'afghanistan', 'thailand', 'vietnam',

    # Americas
    'united states', 'usa', 'america', 'washington', 'new york', 'california',
    'canada', 'toronto', 'vancouver', 'mexico',
    'brazil', 'argentina', 'chile',

    # Africa
    'egypt', 'cairo', 'south africa', 'nigeria', 'kenya'
}

# Nordic context indicators (suggests Nordic response to foreign events)
NORDIC_CONTEXT_KEYWORDS = [
    'denmark responds', 'norwegian authorities', 'swedish defense', 'finnish government',
    'nordic', 'scandinavian', 'nordic countries', 'scandinavian countries',
    'danish foreign minister', 'norwegian prime minister', 'swedish foreign office',
    'meets in copenhagen', 'summit in oslo', 'conference in stockholm',
    'nordic cooperation', 'nordic ministers', 'nordic leaders',
    'denmark comments', 'norway reacts', 'sweden responds', 'finland addresses'
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
    'lahti', 'kuopio',

    # Iceland
    'reykjavík', 'reykjavik', 'keflavík', 'keflavik', 'akureyri',

    # UK
    'london', 'manchester', 'birmingham', 'leeds', 'liverpool', 'glasgow', 'edinburgh',
    'bristol', 'cardiff', 'belfast', 'heathrow', 'gatwick', 'stansted',

    # Germany
    'berlin', 'münchen', 'munich', 'hamburg', 'frankfurt', 'köln', 'cologne', 'stuttgart',
    'düsseldorf', 'dortmund', 'essen', 'leipzig', 'dresden', 'hannover',

    # France
    'paris', 'marseille', 'lyon', 'toulouse', 'nice', 'nantes', 'strasbourg', 'bordeaux',

    # Spain
    'madrid', 'barcelona', 'valencia', 'sevilla', 'bilbao', 'málaga',

    # Italy
    'rome', 'roma', 'milano', 'milan', 'naples', 'napoli', 'turin', 'torino', 'florence', 'firenze',

    # Poland
    'warsaw', 'warszawa', 'krakow', 'kraków', 'wrocław', 'gdańsk', 'poznań',

    # Netherlands
    'amsterdam', 'rotterdam', 'the hague', 'utrecht', 'eindhoven', 'schiphol',

    # Belgium
    'brussels', 'bruxelles', 'antwerp', 'antwerpen', 'bruges', 'brugge', 'ghent', 'gent',

    # Baltics
    'tallinn', 'riga', 'vilnius', 'tartu', 'kaunas',

    # Other European
    'vienna', 'wien', 'zurich', 'zürich', 'geneva', 'genève', 'prague', 'praha',
    'budapest', 'bucharest', 'athens', 'lisbon', 'lisboa', 'dublin'
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


def has_nordic_context(content: str) -> bool:
    """
    Check if content suggests Nordic response to foreign events

    Examples:
    - "Denmark responds to Russian drone attacks in Ukraine"
    - "Nordic ministers meet in Copenhagen to discuss German drone policy"

    Returns:
        True if Nordic context indicators found
    """
    content_lower = content.lower()
    return any(keyword in content_lower for keyword in NORDIC_CONTEXT_KEYWORDS)


def analyze_incident_geography(
    title: str,
    content: str,
    lat: Optional[float],
    lon: Optional[float]
) -> Dict[str, any]:
    """
    Smart geographic analysis with confidence scoring and context detection

    Args:
        title: Incident title
        content: Incident content/narrative
        lat: Latitude coordinate
        lon: Longitude coordinate

    Returns:
        {
            'is_nordic': bool - Should incident be ingested?
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

    # VALIDATION 2: Check for foreign location keywords
    foreign_matches = check_foreign_keywords(full_text)

    if foreign_matches:
        # Check if it's a Nordic response TO foreign events
        if has_nordic_context(content):
            confidence -= 0.4  # Uncertain - might be Nordic article about foreign events
            flags.append('foreign_mentioned_with_nordic_context')
            flags.append(f'foreign_keywords: {", ".join(foreign_matches[:3])}')

            reason = f'Uncertain: Foreign keywords ({", ".join(foreign_matches[:3])}) with Nordic context'
        else:
            # Clear foreign incident
            return {
                'is_nordic': False,
                'confidence': 1.0,
                'reason': f'Foreign incident detected: {", ".join(foreign_matches[:3])}',
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
    is_nordic = confidence >= 0.5

    if is_nordic:
        reason = 'Passed all checks - European incident confirmed'
    else:
        reason = f'Low confidence ({confidence:.2f}) - Non-European content likely'

    return {
        'is_nordic': is_nordic,
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
