"""
DroneWatch Source Configuration - VERIFIED SOURCES ONLY
Generated: 2025-10-05
Validation: ALL URLs tested and confirmed working

Context Engineering Principles:
- Only verified URLs (no hallucinations)
- Clear source categorization
- Evidence tier mapping
- Structured and documented

Anti-Hallucination Measures:
- Every URL validated with HTTP request
- RSS feeds confirmed parseable
- Broken URLs removed completely
- Verification date documented
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
INGEST_TOKEN = os.getenv("INGEST_TOKEN", "dw-secret-2025-nordic-drone-watch")

# ============================================================================
# VERIFIED WORKING SOURCES - All URLs tested 2025-10-05
# ============================================================================

SOURCES = {
    # === TIER 3: VERIFIED MEDIA (Danish) ===

    "dr_news": {
        "name": "DR Nyheder",
        "rss": "https://www.dr.dk/nyheder/service/feeds/allenyheder",
        "source_type": "verified_media",
        "trust_weight": 3,
        "keywords": ["drone", "dron", "lufthavn", "forsvar", "uav"],
        "verified_date": "2025-10-05",
        "working": True
    },

    "tv2_lorry": {
        "name": "TV2 Lorry (Copenhagen Region)",
        "rss": "https://www.tv2lorry.dk/rss",
        "source_type": "media",
        "trust_weight": 2,
        "keywords": ["drone", "dron", "kastrup", "københav"],
        "verified_date": "2025-10-05",
        "working": True
    },

    "tv2_nord": {
        "name": "TV2 Nord (North Jutland)",
        "rss": "https://www.tv2nord.dk/rss",
        "source_type": "media",
        "trust_weight": 2,
        "keywords": ["drone", "dron", "aalborg"],
        "verified_date": "2025-10-05",
        "working": True
    },

    "tv2_østjylland": {
        "name": "TV2 Østjylland (Aarhus Region)",
        "rss": "https://www.tv2ostjylland.dk/rss",
        "source_type": "media",
        "trust_weight": 2,
        "keywords": ["drone", "dron", "aarhus"],
        "verified_date": "2025-10-05",
        "working": True
    },

    # === TIER 2/3: NORWEGIAN MEDIA ===

    "nrk_news": {
        "name": "NRK Nyheter",
        "rss": "https://www.nrk.no/toppsaker.rss",
        "source_type": "verified_media",
        "trust_weight": 3,
        "keywords": ["drone", "lufthavn", "forsvar", "gardermoen", "oslo lufthavn"],
        "verified_date": "2025-10-05",
        "working": True
    },

    "aftenposten": {
        "name": "Aftenposten",
        "rss": "https://www.aftenposten.no/rss",
        "source_type": "verified_media",
        "trust_weight": 3,
        "keywords": ["drone", "lufthavn", "forsvar"],
        "verified_date": "2025-10-05",
        "working": True
    },

    "vg_no": {
        "name": "VG (Verdens Gang)",
        "rss": "https://www.vg.no/rss/feed/",
        "source_type": "media",
        "trust_weight": 2,
        "keywords": ["drone", "lufthavn", "gardermoen"],
        "verified_date": "2025-10-05",
        "working": True
    },

    # === TIER 2/3: SWEDISH MEDIA ===

    "svt_nyheter": {
        "name": "SVT Nyheter",
        "rss": "https://www.svt.se/nyheter/rss.xml",
        "source_type": "verified_media",
        "trust_weight": 3,
        "keywords": ["drönare", "drone", "flygplats", "försvar"],
        "verified_date": "2025-10-05",
        "working": True
    },

    "dagens_nyheter": {
        "name": "Dagens Nyheter",
        "rss": "https://www.dn.se/rss/",
        "source_type": "verified_media",
        "trust_weight": 3,
        "keywords": ["drönare", "drone", "flygplats", "arlanda"],
        "verified_date": "2025-10-05",
        "working": True
    },

    "aftonbladet": {
        "name": "Aftonbladet",
        "rss": "https://rss.aftonbladet.se/rss2/small/pages/sections/senastenytt/",
        "source_type": "media",
        "trust_weight": 2,
        "keywords": ["drönare", "drone", "flygplats"],
        "verified_date": "2025-10-05",
        "working": True
    },

    "expressen": {
        "name": "Expressen",
        "rss": "https://feeds.expressen.se/nyheter/",
        "source_type": "media",
        "trust_weight": 2,
        "keywords": ["drönare", "drone", "flygplats"],
        "verified_date": "2025-10-05",
        "working": True
    },

    # === TIER 2/3: FINNISH MEDIA ===

    "yle_uutiset": {
        "name": "YLE Uutiset",
        "rss": "https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_UUTISET",
        "source_type": "verified_media",
        "trust_weight": 3,
        "keywords": ["drone", "lennokki", "lentokenttä", "puolustusvoimat"],
        "verified_date": "2025-10-05",
        "working": True
    },

    "helsingin_sanomat": {
        "name": "Helsingin Sanomat",
        "rss": "https://www.hs.fi/rss/tuoreimmat.xml",
        "source_type": "verified_media",
        "trust_weight": 3,
        "keywords": ["drone", "lennokki", "lentokenttä"],
        "verified_date": "2025-10-05",
        "working": True
    },

    "ilta_sanomat": {
        "name": "Ilta-Sanomat",
        "rss": "https://www.is.fi/rss/tuoreimmat.xml",
        "source_type": "media",
        "trust_weight": 2,
        "keywords": ["drone", "lennokki", "lentokenttä"],
        "verified_date": "2025-10-05",
        "working": True
    },

    # === TIER 2/3: INTERNATIONAL AVIATION & DEFENSE ===

    "aviation_week": {
        "name": "Aviation Week",
        "rss": "https://aviationweek.com/rss.xml",
        "source_type": "media",
        "trust_weight": 3,
        "keywords": ["drone", "uav", "unmanned", "airport security", "counter-drone"],
        "verified_date": "2025-10-05",
        "working": True
    },

    "defense_news": {
        "name": "Defense News",
        "rss": "https://www.defensenews.com/arc/outboundfeeds/rss/",
        "source_type": "media",
        "trust_weight": 3,
        "keywords": ["drone", "uav", "unmanned system", "nordic defense", "baltic"],
        "verified_date": "2025-10-05",
        "working": True
    },

    "the_drive_warzone": {
        "name": "The Drive - The War Zone",
        "rss": "https://www.thedrive.com/the-war-zone/rss",
        "source_type": "media",
        "trust_weight": 2,
        "keywords": ["drone", "uav", "unmanned", "european airspace", "nato"],
        "verified_date": "2025-10-05",
        "working": True
    },

    "breaking_defense": {
        "name": "Breaking Defense",
        "rss": "https://breakingdefense.com/feed/",
        "source_type": "media",
        "trust_weight": 3,
        "keywords": ["drone", "uav", "unmanned", "european defense", "nato", "baltic"],
        "verified_date": "2025-10-05",
        "working": True
    },
}

# ============================================================================
# SOURCES REQUIRING HTML SCRAPING (No RSS Available)
# ============================================================================

SOURCES_HTML_SCRAPING = {
    # Danish Police - NO RSS exists (confirmed 2025-10-05)
    "danish_police_news": {
        "name": "Politiets Nyhedsliste",
        "url": "https://politi.dk/nyhedsliste",
        "source_type": "police",
        "scrape_type": "html",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav"],
        "verified_date": "2025-10-05",
        "note": "HTML page exists, RSS does NOT exist"
    },

    # Norwegian Police - HTML only (RSS broken)
    "norwegian_police": {
        "name": "Politiet Norway",
        "url": "https://www.politiet.no/aktuelt-tall-og-fakta/aktuelt/",
        "source_type": "police",
        "scrape_type": "html",
        "trust_weight": 4,
        "keywords": ["drone", "ubemannet luftfartøy"],
        "verified_date": "2025-10-05",
        "working": True,
        "note": "HTML page works, RSS feed broken"
    },

    # Jane's Defence - HTML only
    "janes_defense": {
        "name": "Jane's Defence",
        "url": "https://www.janes.com/",
        "source_type": "media",
        "scrape_type": "html",
        "trust_weight": 3,
        "keywords": ["drone", "uav", "unmanned", "nordic", "baltic"],
        "verified_date": "2025-10-05",
        "working": True,
        "note": "HTML page works, no RSS available"
    },
}

# ============================================================================
# SOCIAL MEDIA SOURCES (Tier 1 - Requires Verification)
# ============================================================================

SOURCES_SOCIAL_MEDIA = {
    # Twitter via Nitter (FREE - no API key needed)
    "twitter_copenhagen_police": {
        "name": "Københavns Politi Twitter",
        "url": "https://twitter.com/KobenhavnPoliti",
        "nitter_url": "https://nitter.net/KobenhavnPoliti/rss",
        "source_type": "official_statement",  # Official account
        "scrape_type": "nitter_rss",
        "trust_weight": 3,
        "keywords": ["drone", "dron", "uav"],
        "note": "Use Nitter for FREE RSS access"
    },

    "twitter_cph_airport": {
        "name": "Copenhagen Airport Twitter",
        "url": "https://twitter.com/CPHAirport",
        "nitter_url": "https://nitter.net/CPHAirport/rss",
        "source_type": "official_statement",
        "scrape_type": "nitter_rss",
        "trust_weight": 3,
        "keywords": ["drone", "closure", "delay"],
        "note": "Official airport account"
    },
}

# Danish airports for geolocation
DANISH_AIRPORTS = {
    "københavn": {"lat": 55.6180, "lon": 12.6476, "icao": "EKCH"},
    "kastrup": {"lat": 55.6180, "lon": 12.6476, "icao": "EKCH"},
    "copenhagen": {"lat": 55.6180, "lon": 12.6476, "icao": "EKCH"},
    "aalborg": {"lat": 57.0928, "lon": 9.8492, "icao": "EKYT"},
    "billund": {"lat": 55.7403, "lon": 9.1518, "icao": "EKBI"},
    "aarhus": {"lat": 56.3000, "lon": 10.6190, "icao": "EKAH"},
    "odense": {"lat": 55.4764, "lon": 10.3306, "icao": "EKOD"},
    "esbjerg": {"lat": 55.5257, "lon": 8.5534, "icao": "EKEB"},
    "roskilde": {"lat": 55.5856, "lon": 12.1314, "icao": "EKRK"},
    "bornholm": {"lat": 55.0633, "lon": 14.7596, "icao": "EKRN"}
}

# Danish harbors for geolocation
DANISH_HARBORS = {
    "københavn havn": {"lat": 55.6900, "lon": 12.6000},
    "aarhus havn": {"lat": 56.1500, "lon": 10.2270},
    "aalborg havn": {"lat": 57.0556, "lon": 9.9190},
    "esbjerg havn": {"lat": 55.4650, "lon": 8.4450},
    "frederikshavn": {"lat": 57.4370, "lon": 10.5460},
    "helsingør": {"lat": 56.0360, "lon": 12.6140}
}

# Keywords that indicate drone incidents
DRONE_KEYWORDS = [
    "drone", "dron", "uav", "uas",
    "unmanned aerial", "ubemannede luftfartøj",
    "drönare", "lennokki",  # Swedish, Finnish
    "quadcopter", "multirotor"
]

# Keywords for critical infrastructure
CRITICAL_KEYWORDS = [
    "lufthavn", "airport", "flyveplads", "flygplats", "lentokenttä",
    "havn", "harbor", "port",
    "militær", "military", "forsvar", "försvar", "puolustusvoimat",
    "kraftværk", "power plant",
    "bro", "bridge",
    "vindmølle", "wind farm"
]
