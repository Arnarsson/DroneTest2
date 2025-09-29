"""
Ingestion configuration for DroneWatch
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
INGEST_TOKEN = os.getenv("INGEST_TOKEN", "dw-secret-2025-nordic-drone-watch")

# Source configurations
SOURCES = {
    "danish_police": {
        "name": "Nordjyllands Politi",
        "url": "https://politi.dk/nordjyllands-politi/nyhedsliste",
        "rss": "https://politi.dk/nordjyllands-politi/nyhedsliste/rss.xml",
        "type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav", "luftfartøj", "lufthavn", "airport"]
    },
    "copenhagen_police": {
        "name": "Københavns Politi",
        "url": "https://politi.dk/koebenhavns-politi/nyhedsliste",
        "rss": "https://politi.dk/koebenhavns-politi/nyhedsliste/rss.xml",
        "type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav", "luftfartøj", "kastrup"]
    },
    "dr_news": {
        "name": "DR Nyheder",
        "rss": "https://www.dr.dk/nyheder/service/feeds/allenyheder",
        "type": "media",
        "trust_weight": 3,
        "keywords": ["drone", "dron", "lufthavn", "forsvar"]
    },
    "tv2_news": {
        "name": "TV2 News",
        "rss": "https://feeds.tv2.dk/nyheder/rss",
        "type": "media",
        "trust_weight": 3,
        "keywords": ["drone", "dron", "luftrum"]
    }
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
    "quadcopter", "multirotor"
]

# Keywords for critical infrastructure
CRITICAL_KEYWORDS = [
    "lufthavn", "airport", "flyveplads",
    "havn", "harbor", "port",
    "militær", "military", "forsvar",
    "kraftværk", "power plant",
    "bro", "bridge",
    "vindmølle", "wind farm"
]