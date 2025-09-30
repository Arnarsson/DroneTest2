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
    # === POLICE SOURCES (All Danish Police Districts) ===
    "nordjyllands_police": {
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
    "vestsjællands_police": {
        "name": "Midt- og Vestsjællands Politi",
        "url": "https://politi.dk/midt-og-vestsjaellands-politi/nyhedsliste",
        "rss": "https://politi.dk/midt-og-vestsjaellands-politi/nyhedsliste/rss.xml",
        "type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav", "luftfartøj"]
    },
    "sydsjællands_police": {
        "name": "Sydsjællands og Lolland-Falsters Politi",
        "url": "https://politi.dk/sydsjaellands-og-lolland-falsters-politi/nyhedsliste",
        "rss": "https://politi.dk/sydsjaellands-og-lolland-falsters-politi/nyhedsliste/rss.xml",
        "type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav", "luftfartøj"]
    },
    "fyn_police": {
        "name": "Fyns Politi",
        "url": "https://politi.dk/fyns-politi/nyhedsliste",
        "rss": "https://politi.dk/fyns-politi/nyhedsliste/rss.xml",
        "type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav", "luftfartøj", "odense"]
    },
    "syddanmark_police": {
        "name": "Syd- og Sønderjyllands Politi",
        "url": "https://politi.dk/syd-og-soenderjyllands-politi/nyhedsliste",
        "rss": "https://politi.dk/syd-og-soenderjyllands-politi/nyhedsliste/rss.xml",
        "type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav", "luftfartøj", "esbjerg", "billund"]
    },
    "sydøstjyllands_police": {
        "name": "Sydøstjyllands Politi",
        "url": "https://politi.dk/sydoestjyllands-politi/nyhedsliste",
        "rss": "https://politi.dk/sydoestjyllands-politi/nyhedsliste/rss.xml",
        "type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav", "luftfartøj"]
    },
    "østjyllands_police": {
        "name": "Østjyllands Politi",
        "url": "https://politi.dk/oestjyllands-politi/nyhedsliste",
        "rss": "https://politi.dk/oestjyllands-politi/nyhedsliste/rss.xml",
        "type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav", "luftfartøj", "aarhus"]
    },
    "midtjyllands_police": {
        "name": "Midt- og Vestjyllands Politi",
        "url": "https://politi.dk/midt-og-vestjyllands-politi/nyhedsliste",
        "rss": "https://politi.dk/midt-og-vestjyllands-politi/nyhedsliste/rss.xml",
        "type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav", "luftfartøj"]
    },
    "nordjyllands_police": {
        "name": "Nordjyllands Politi",
        "url": "https://politi.dk/nordjyllands-politi/nyhedsliste",
        "rss": "https://politi.dk/nordjyllands-politi/nyhedsliste/rss.xml",
        "type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav", "luftfartøj", "aalborg"]
    },
    "nordsjællands_police": {
        "name": "Nordsjællands Politi",
        "url": "https://politi.dk/nordsjaellands-politi/nyhedsliste",
        "rss": "https://politi.dk/nordsjaellands-politi/nyhedsliste/rss.xml",
        "type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav", "luftfartøj", "helsingør"]
    },
    "bornholms_police": {
        "name": "Bornholms Politi",
        "url": "https://politi.dk/bornholms-politi/nyhedsliste",
        "rss": "https://politi.dk/bornholms-politi/nyhedsliste/rss.xml",
        "type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav", "luftfartøj"]
    },

    # === NATIONAL NEWS SOURCES ===
    "dr_news": {
        "name": "DR Nyheder",
        "rss": "https://www.dr.dk/nyheder/service/feeds/allenyheder",
        "type": "media",
        "trust_weight": 3,
        "keywords": ["drone", "dron", "lufthavn", "forsvar", "uav"]
    },
    "tv2_news": {
        "name": "TV2 News",
        "rss": "https://feeds.tv2.dk/nyheder/rss",
        "type": "media",
        "trust_weight": 3,
        "keywords": ["drone", "dron", "luftrum", "lufthavn"]
    },
    "berlingske": {
        "name": "Berlingske",
        "rss": "https://www.berlingske.dk/rss",
        "type": "media",
        "trust_weight": 3,
        "keywords": ["drone", "dron", "lufthavn", "forsvar"]
    },
    "jyllands_posten": {
        "name": "Jyllands-Posten",
        "rss": "https://jyllands-posten.dk/rss",
        "type": "media",
        "trust_weight": 3,
        "keywords": ["drone", "dron", "lufthavn", "luftrum"]
    },
    "politiken": {
        "name": "Politiken",
        "rss": "https://politiken.dk/rss/",
        "type": "media",
        "trust_weight": 3,
        "keywords": ["drone", "dron", "lufthavn"]
    },

    # === REGIONAL NEWS ===
    "tv2_lorry": {
        "name": "TV2 Lorry (Copenhagen Region)",
        "rss": "https://www.tv2lorry.dk/rss",
        "type": "media",
        "trust_weight": 2,
        "keywords": ["drone", "dron", "kastrup", "københav"]
    },
    "tv2_nord": {
        "name": "TV2 Nord (North Jutland)",
        "rss": "https://www.tv2nord.dk/rss",
        "type": "media",
        "trust_weight": 2,
        "keywords": ["drone", "dron", "aalborg"]
    },
    "tv2_østjylland": {
        "name": "TV2 Østjylland (Aarhus Region)",
        "rss": "https://www.tv2ostjylland.dk/rss",
        "type": "media",
        "trust_weight": 2,
        "keywords": ["drone", "dron", "aarhus"]
    },

    # === NORWEGIAN SOURCES ===
    "politiet_no": {
        "name": "Politiet (Norwegian National Police)",
        "url": "https://www.politiet.no/aktuelt-tall-og-fakta/aktuelt/",
        "rss": "https://www.politiet.no/aktuelt-tall-og-fakta/aktuelt/rss/",
        "type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "ubemannet luftfartøy", "uav", "lufthavn", "flyplass"]
    },
    "nrk_news": {
        "name": "NRK Nyheter",
        "rss": "https://www.nrk.no/toppsaker.rss",
        "type": "media",
        "trust_weight": 3,
        "keywords": ["drone", "lufthavn", "forsvar", "gardermoen", "oslo lufthavn"]
    },
    "aftenposten": {
        "name": "Aftenposten",
        "rss": "https://www.aftenposten.no/rss",
        "type": "media",
        "trust_weight": 3,
        "keywords": ["drone", "lufthavn", "forsvar"]
    },
    "vg_no": {
        "name": "VG (Verdens Gang)",
        "rss": "https://www.vg.no/rss/feed/",
        "type": "media",
        "trust_weight": 2,
        "keywords": ["drone", "lufthavn", "gardermoen"]
    },
    "dagbladet_no": {
        "name": "Dagbladet",
        "rss": "https://www.dagbladet.no/rss",
        "type": "media",
        "trust_weight": 2,
        "keywords": ["drone", "lufthavn"]
    },

    # === SWEDISH SOURCES ===
    "polisen_se": {
        "name": "Polisen (Swedish National Police)",
        "url": "https://polisen.se/aktuellt/nyheter/",
        "rss": "https://polisen.se/aktuellt/rss/",
        "type": "police",
        "trust_weight": 4,
        "keywords": ["drönare", "drone", "flygplats", "arlanda", "bromma"]
    },
    "svt_nyheter": {
        "name": "SVT Nyheter",
        "rss": "https://www.svt.se/nyheter/rss.xml",
        "type": "media",
        "trust_weight": 3,
        "keywords": ["drönare", "drone", "flygplats", "försvar"]
    },
    "dagens_nyheter": {
        "name": "Dagens Nyheter",
        "rss": "https://www.dn.se/rss/",
        "type": "media",
        "trust_weight": 3,
        "keywords": ["drönare", "drone", "flygplats", "arlanda"]
    },
    "svenska_dagbladet": {
        "name": "Svenska Dagbladet",
        "rss": "https://www.svd.se/rss.xml",
        "type": "media",
        "trust_weight": 3,
        "keywords": ["drönare", "drone", "flygplats"]
    },
    "aftonbladet": {
        "name": "Aftonbladet",
        "rss": "https://rss.aftonbladet.se/rss2/small/pages/sections/senastenytt/",
        "type": "media",
        "trust_weight": 2,
        "keywords": ["drönare", "drone", "flygplats"]
    },
    "expressen": {
        "name": "Expressen",
        "rss": "https://feeds.expressen.se/nyheter/",
        "type": "media",
        "trust_weight": 2,
        "keywords": ["drönare", "drone", "flygplats"]
    },

    # === FINNISH SOURCES ===
    "poliisi_fi": {
        "name": "Poliisi (Finnish National Police)",
        "url": "https://poliisi.fi/tietoa-poliisista/tiedotteet",
        "rss": "https://poliisi.fi/rss/tiedotteet",
        "type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "lennokki", "miehittämätön ilma-alus", "lentokenttä", "helsinki-vantaa"]
    },
    "yle_uutiset": {
        "name": "YLE Uutiset",
        "rss": "https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_UUTISET",
        "type": "media",
        "trust_weight": 3,
        "keywords": ["drone", "lennokki", "lentokenttä", "puolustusvoimat"]
    },
    "helsingin_sanomat": {
        "name": "Helsingin Sanomat",
        "rss": "https://www.hs.fi/rss/tuoreimmat.xml",
        "type": "media",
        "trust_weight": 3,
        "keywords": ["drone", "lennokki", "lentokenttä"]
    },
    "ilta_sanomat": {
        "name": "Ilta-Sanomat",
        "rss": "https://www.is.fi/rss/tuoreimmat.xml",
        "type": "media",
        "trust_weight": 2,
        "keywords": ["drone", "lennokki", "lentokenttä"]
    },

    # === INTERNATIONAL AVIATION & DEFENSE ===
    "flightglobal": {
        "name": "FlightGlobal",
        "rss": "https://www.flightglobal.com/rss/articles/all/feed.xml",
        "type": "media",
        "trust_weight": 3,
        "keywords": ["drone", "uav", "uas", "airport", "airspace", "security"]
    },
    "aviation_week": {
        "name": "Aviation Week",
        "rss": "https://aviationweek.com/rss.xml",
        "type": "media",
        "trust_weight": 3,
        "keywords": ["drone", "uav", "unmanned", "airport security", "counter-drone"]
    },
    "defense_news": {
        "name": "Defense News",
        "rss": "https://www.defensenews.com/arc/outboundfeeds/rss/",
        "type": "media",
        "trust_weight": 3,
        "keywords": ["drone", "uav", "unmanned system", "nordic defense", "baltic"]
    },
    "janes_defense": {
        "name": "Jane's Defence",
        "url": "https://www.janes.com/",
        "type": "media",
        "trust_weight": 3,
        "keywords": ["drone", "uav", "unmanned", "nordic", "baltic", "european defense"]
    },
    "the_drive_warzone": {
        "name": "The Drive - The War Zone",
        "rss": "https://www.thedrive.com/the-war-zone/rss",
        "type": "media",
        "trust_weight": 2,
        "keywords": ["drone", "uav", "unmanned", "european airspace", "nato"]
    },
    "breaking_defense": {
        "name": "Breaking Defense",
        "rss": "https://breakingdefense.com/feed/",
        "type": "media",
        "trust_weight": 3,
        "keywords": ["drone", "uav", "unmanned", "european defense", "nato", "baltic"]
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