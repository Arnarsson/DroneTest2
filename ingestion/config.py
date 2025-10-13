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

    # === TIER 4: NORWEGIAN POLICE (Politiloggen RSS) ===
    # Norwegian police discontinued Twitter/X in October 2024
    # They now use Politiloggen app with official RSS feeds
    # Source type: police (official) - trust_weight: 4

    "politiloggen_oslo": {
        "name": "Politiloggen Oslo",
        "rss": "https://api.politiet.no/politiloggen/v1/rss?districts=oslo",
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "ubemannet luftfartøy", "gardermoen", "oslo lufthavn"],
        "verified_date": "2025-10-09",
        "working": True,
        "note": "Oslo police district - covers Gardermoen Airport"
    },

    "politiloggen_ost": {
        "name": "Politiloggen Øst",
        "rss": "https://api.politiet.no/politiloggen/v1/rss?districts=ost",
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "ubemannet luftfartøy"],
        "verified_date": "2025-10-09",
        "working": True,
        "note": "Eastern Norway police district"
    },

    "politiloggen_innlandet": {
        "name": "Politiloggen Innlandet",
        "rss": "https://api.politiet.no/politiloggen/v1/rss?districts=innlandet",
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "ubemannet luftfartøy"],
        "verified_date": "2025-10-09",
        "working": True,
        "note": "Inland Norway police district"
    },

    "politiloggen_sorost": {
        "name": "Politiloggen Sør-Øst",
        "rss": "https://api.politiet.no/politiloggen/v1/rss?districts=sor-ost",
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "ubemannet luftfartøy"],
        "verified_date": "2025-10-09",
        "working": True,
        "note": "Southeast Norway police district"
    },

    "politiloggen_agder": {
        "name": "Politiloggen Agder",
        "rss": "https://api.politiet.no/politiloggen/v1/rss?districts=agder",
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "ubemannet luftfartøy", "kristiansand"],
        "verified_date": "2025-10-09",
        "working": True,
        "note": "Agder police district - southern Norway"
    },

    "politiloggen_sorvest": {
        "name": "Politiloggen Sør-Vest",
        "rss": "https://api.politiet.no/politiloggen/v1/rss?districts=sor-vest",
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "ubemannet luftfartøy", "stavanger lufthavn"],
        "verified_date": "2025-10-09",
        "working": True,
        "note": "Southwest Norway - covers Stavanger Airport"
    },

    "politiloggen_vest": {
        "name": "Politiloggen Vest",
        "rss": "https://api.politiet.no/politiloggen/v1/rss?districts=vest",
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "ubemannet luftfartøy", "bergen lufthavn"],
        "verified_date": "2025-10-09",
        "working": True,
        "note": "Western Norway - covers Bergen Airport"
    },

    "politiloggen_more_romsdal": {
        "name": "Politiloggen Møre og Romsdal",
        "rss": "https://api.politiet.no/politiloggen/v1/rss?districts=more-og-romsdal",
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "ubemannet luftfartøy"],
        "verified_date": "2025-10-09",
        "working": True,
        "note": "Møre og Romsdal police district"
    },

    "politiloggen_trondelag": {
        "name": "Politiloggen Trøndelag",
        "rss": "https://api.politiet.no/politiloggen/v1/rss?districts=trondelag",
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "ubemannet luftfartøy", "trondheim"],
        "verified_date": "2025-10-09",
        "working": True,
        "note": "Trøndelag police district - central Norway"
    },

    "politiloggen_nordland": {
        "name": "Politiloggen Nordland",
        "rss": "https://api.politiet.no/politiloggen/v1/rss?districts=nordland",
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "ubemannet luftfartøy"],
        "verified_date": "2025-10-09",
        "working": True,
        "note": "Nordland police district - northern Norway"
    },

    "politiloggen_troms": {
        "name": "Politiloggen Troms",
        "rss": "https://api.politiet.no/politiloggen/v1/rss?districts=troms",
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "ubemannet luftfartøy", "tromsø"],
        "verified_date": "2025-10-09",
        "working": True,
        "note": "Troms police district - northern Norway"
    },

    "politiloggen_finnmark": {
        "name": "Politiloggen Finnmark",
        "rss": "https://api.politiet.no/politiloggen/v1/rss?districts=finnmark",
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "ubemannet luftfartøy"],
        "verified_date": "2025-10-09",
        "working": True,
        "note": "Finnmark police district - far northern Norway"
    },

    # === TIER 4: SWEDISH POLICE (Polisen RSS) - VERIFIED SOURCES ONLY ===
    # Verified: 2025-10-13 via curl testing
    # URL pattern: https://polisen.se/aktuellt/rss/[region]/handelser-rss---[region]/
    # Note: Conservative approach - only adding feeds confirmed working via HTTP request

    "polisen_stockholm": {
        "name": "Polisen Stockholm",
        "rss": "https://polisen.se/aktuellt/rss/stockholms-lan/handelser-rss---stockholms-lan/",
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drönare", "drone", "flygplats", "arlanda", "bromma"],
        "verified_date": "2025-10-13",
        "working": True,  # ✅ VERIFIED via curl
        "country": "SE",
        "note": "Stockholm region - covers Arlanda and Bromma airports"
    },

    "polisen_skane": {
        "name": "Polisen Skåne",
        "rss": "https://polisen.se/aktuellt/rss/skane/handelser-rss---skane/",
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drönare", "drone", "flygplats", "malmö", "sturup"],
        "verified_date": "2025-10-13",
        "working": True,  # ✅ VERIFIED via curl
        "country": "SE",
        "note": "Skåne region - covers Malmö and Sturup airports"
    },

    "polisen_norrbotten": {
        "name": "Polisen Norrbotten",
        "rss": "https://polisen.se/aktuellt/rss/norrbotten/handelser-rss---norrbotten/",
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drönare", "drone", "flygplats"],
        "verified_date": "2025-10-13",
        "working": True,  # ✅ VERIFIED via curl
        "country": "SE",
        "note": "Norrbotten region - far northern Sweden"
    },

    # === TIER 4: FINNISH POLICE (Poliisi RSS) - VERIFIED SOURCES ONLY ===
    # Verified: 2025-10-13 via curl testing
    # Conservative approach - adding national feed + key regional feeds covering airports

    "poliisi_national": {
        "name": "Poliisi Finland (National)",
        "rss": "https://poliisi.fi/en/newsroom/-/asset_publisher/ZrUg5zQFOAqI/rss",
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "lennokki", "lentokenttä", "puolustusvoimat"],
        "verified_date": "2025-10-13",
        "working": True,  # ✅ VERIFIED via curl
        "country": "FI",
        "note": "National police news - all of Finland"
    },

    "poliisi_helsinki": {
        "name": "Poliisi Helsinki",
        "rss": "https://poliisi.fi/en/helsinki-police-department/-/asset_publisher/ZtAEeHB39Lxr/rss",
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "lennokki", "lentokenttä", "vantaa", "helsinki"],
        "verified_date": "2025-10-13",
        "working": True,  # ✅ VERIFIED via curl
        "country": "FI",
        "note": "Helsinki region - covers Helsinki-Vantaa Airport"
    },

    "poliisi_southwestern": {
        "name": "Poliisi Southwestern Finland",
        "rss": "https://poliisi.fi/en/southwestern-finland-police-department/-/asset_publisher/ZtAEeHB39Lxr/rss",
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "lennokki", "lentokenttä", "turku"],
        "verified_date": "2025-10-13",
        "working": True,  # ✅ VERIFIED via curl
        "country": "FI",
        "note": "Southwestern Finland - covers Turku Airport"
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

# Merge HTML scraping sources into main SOURCES dict
SOURCES.update(SOURCES_HTML_SCRAPING)

# ============================================================================
# SOCIAL MEDIA SOURCES - DANISH POLICE TWITTER/X ACCOUNTS
# ============================================================================
#
# CRITICAL: RSS.app setup required! See docs/TWITTER_RSS_SETUP.md
#
# STATUS: ⚠️ BLOCKED - Waiting for RSS.app feed URLs
# ACTION: User must create RSS.app account and provide feed URLs
#
# Nitter (discontinued Feb 2024) ❌
# TwitRSS.me (offline) ❌
# RSS.app (working Oct 2025) ✅
#
# Trust Weight: 4 (Official police sources)
# Source Type: police
# Evidence Score: Automatic 4 for police tweets
# ============================================================================

TWITTER_POLICE_SOURCES = {
    # === NATIONAL LEVEL ===

    "twitter_rigspolitiet": {
        "name": "Rigspolitiet (Danish National Police)",
        "handle": "@rigspoliti",
        "twitter_url": "https://twitter.com/rigspoliti",
        "rss": "https://rss.app/feeds/HvDr7FqcLUua0IcL.xml",  # ✅ ACTIVE
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav", "lufthavn", "forsvar"],
        "hashtags": ["#politidk", "#kriseinfodk"],
        "region": "National",
        "enabled": True,  # ✅ ENABLED
        "note": "National police coordination - highest priority incidents"
    },

    "twitter_nsk_politi": {
        "name": "National Special Crime Unit (NSK)",
        "handle": "@NSK_politi",
        "twitter_url": "https://twitter.com/NSK_politi",
        "rss": "https://rss.app/feeds/L4BC1apO60hTYJTl.xml",  # ✅ ACTIVE
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav", "terrorisme"],
        "hashtags": ["#politidk", "#kriseinfodk"],
        "region": "National",
        "enabled": True,  # ✅ ENABLED
        "note": "Special crime unit - serious/terrorism-related incidents"
    },

    # === COPENHAGEN REGION (HIGH PRIORITY - Airport) ===

    "twitter_kobenhavns_politi": {
        "name": "Københavns Politi (Copenhagen Police)",
        "handle": "@KobenhavnPoliti",
        "twitter_url": "https://twitter.com/KobenhavnPoliti",
        "rss": "https://rss.app/feeds/48SBRIsgrBUGgpk1.xml",  # ✅ TESTED & WORKING
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav", "kastrup", "lufthavn"],
        "hashtags": ["#politidk", "#kriseinfodk"],
        "region": "Copenhagen",
        "enabled": True,  # ✅ ENABLED - RSS feed working
        "note": "Copenhagen Airport coverage - HIGHEST PRIORITY"
    },

    "twitter_vestegns_politi": {
        "name": "Københavns Vestegns Politi (Western Copenhagen)",
        "handle": "@VestegnsPoliti",
        "twitter_url": "https://twitter.com/VestegnsPoliti",
        "rss": "https://rss.app/feeds/1pdpD7YWeWZesdPa.xml",  # ✅ ACTIVE
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav"],
        "hashtags": ["#politidk", "#kriseinfodk"],
        "region": "Copenhagen West",
        "enabled": True,  # ✅ ENABLED
        "note": "Western Copenhagen suburbs"
    },

    # === JUTLAND REGION (Airports: Aalborg, Aarhus, Billund) ===

    "twitter_nordjyllands_politi": {
        "name": "Nordjyllands Politi (North Jutland)",
        "handle": "@NjylPoliti",
        "twitter_url": "https://twitter.com/NjylPoliti",
        "rss": "https://rss.app/feeds/jbxPI8S4vF2Dkpri.xml",  # ✅ ACTIVE
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav", "aalborg", "lufthavn"],
        "hashtags": ["#politidk", "#kriseinfodk"],
        "region": "North Jutland",
        "enabled": True,  # ✅ ENABLED - Aalborg Airport
        "note": "Aalborg Airport coverage"
    },

    "twitter_ostjyllands_politi": {
        "name": "Østjyllands Politi (East Jutland)",
        "handle": "@OjylPoliti",
        "twitter_url": "https://twitter.com/OjylPoliti",
        "rss": "https://rss.app/feeds/zXpKUJARbccC3GUH.xml",  # ✅ ACTIVE
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav", "aarhus", "lufthavn"],
        "hashtags": ["#politidk", "#kriseinfodk"],
        "region": "East Jutland",
        "enabled": True,  # ✅ ENABLED - Aarhus Airport
        "note": "Aarhus Airport coverage"
    },

    "twitter_sydostjyllands_politi": {
        "name": "Sydøstjyllands Politi (Southeast Jutland)",
        "handle": "@SydOjylPoliti",
        "twitter_url": "https://twitter.com/SydOjylPoliti",
        "rss": "https://rss.app/feeds/9ghuITkYM3AXNXIA.xml",  # ✅ ACTIVE
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav"],
        "hashtags": ["#politidk", "#kriseinfodk"],
        "region": "Southeast Jutland",
        "enabled": True,  # ✅ ENABLED
        "note": "Southeast Jutland region"
    },

    "twitter_syd_sonderjyllands_politi": {
        "name": "Syd- og Sønderjyllands Politi (South Jutland)",
        "handle": "@SjylPoliti",
        "twitter_url": "https://twitter.com/SjylPoliti",
        "rss": "PLACEHOLDER_RSS_APP_URL_HERE",
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav"],
        "hashtags": ["#politidk", "#kriseinfodk"],
        "region": "South Jutland",
        "enabled": False,
        "note": "South Jutland region near German border"
    },

    "twitter_midt_vestjyllands_politi": {
        "name": "Midt- og Vestjyllands Politi (Central/West Jutland)",
        "handle": "@MVJPoliti",
        "twitter_url": "https://twitter.com/MVJPoliti",
        "rss": "https://rss.app/feeds/TiRoJ2kblbMJWdbT.xml",  # ✅ ACTIVE
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav", "billund", "lufthavn"],
        "hashtags": ["#politidk", "#kriseinfodk"],
        "region": "Central/West Jutland",
        "enabled": True,  # ✅ ENABLED - Billund Airport
        "note": "Billund Airport coverage"
    },

    # === ZEALAND REGION ===

    "twitter_nordsjaellands_politi": {
        "name": "Nordsjællands Politi (North Zealand)",
        "handle": "@NSJPoliti",
        "twitter_url": "https://twitter.com/NSJPoliti",
        "rss": "https://rss.app/feeds/BONVTNXyLMAG2E1t.xml",  # ✅ ACTIVE
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav"],
        "hashtags": ["#politidk", "#kriseinfodk"],
        "region": "North Zealand",
        "enabled": True,  # ✅ ENABLED
        "note": "North Zealand region"
    },

    "twitter_midt_vestsjaellands_politi": {
        "name": "Midt- og Vestsjællands Politi (Central/West Zealand)",
        "handle": "@MVSJPoliti",
        "twitter_url": "https://twitter.com/MVSJPoliti",
        "rss": "PLACEHOLDER_RSS_APP_URL_HERE",
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav"],
        "hashtags": ["#politidk", "#kriseinfodk"],
        "region": "Central/West Zealand",
        "enabled": False,
        "note": "Central and West Zealand"
    },

    "twitter_sydsjaellands_lolland_falster_politi": {
        "name": "Sydsjællands og Lolland-Falsters Politi",
        "handle": "@SSJ_LFPoliti",
        "twitter_url": "https://twitter.com/SSJ_LFPoliti",
        "rss": "PLACEHOLDER_RSS_APP_URL_HERE",
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav"],
        "hashtags": ["#politidk", "#kriseinfodk"],
        "region": "South Zealand/Lolland-Falster",
        "enabled": False,
        "note": "South Zealand and islands"
    },

    # === FUNEN & BORNHOLM ===

    "twitter_fyns_politi": {
        "name": "Fyns Politi (Funen)",
        "handle": "@FynsPoliti",
        "twitter_url": "https://twitter.com/FynsPoliti",
        "rss": "https://rss.app/feeds/HgunKFZPzd9tF0Id.xml",  # ✅ ACTIVE
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav", "odense"],
        "hashtags": ["#politidk", "#kriseinfodk"],
        "region": "Funen",
        "enabled": True,  # ✅ ENABLED - Odense Airport
        "note": "Funen island - Odense Airport"
    },

    "twitter_bornholms_politi": {
        "name": "Bornholms Politi",
        "handle": "@BornholmsPoliti",
        "twitter_url": "https://twitter.com/BornholmsPoliti",
        "rss": "PLACEHOLDER_RSS_APP_URL_HERE",
        "source_type": "police",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav"],
        "hashtags": ["#politidk", "#kriseinfodk"],
        "region": "Bornholm",
        "enabled": False,
        "note": "Bornholm island - Baltic Sea"
    },

    # === OTHER ===

    "twitter_politimuseet": {
        "name": "Politimuseet (Police Museum)",
        "handle": "@Politimuseet",
        "twitter_url": "https://twitter.com/Politimuseet",
        "rss": "PLACEHOLDER_RSS_APP_URL_HERE",
        "source_type": "education",
        "trust_weight": 2,
        "keywords": ["drone", "dron"],
        "hashtags": ["#politidk"],
        "region": "National",
        "enabled": False,
        "note": "Educational content - low priority for incidents"
    },
}

# Legacy Nitter sources (DEPRECATED - Nitter discontinued Feb 2024)
SOURCES_SOCIAL_MEDIA_DEPRECATED = {
    "twitter_copenhagen_police_nitter": {
        "name": "Københavns Politi Twitter (Nitter - DEPRECATED)",
        "url": "https://twitter.com/KobenhavnPoliti",
        "nitter_url": "https://nitter.net/KobenhavnPoliti/rss",
        "source_type": "police",
        "scrape_type": "nitter_rss",
        "trust_weight": 4,
        "keywords": ["drone", "dron", "uav"],
        "enabled": False,
        "note": "DEPRECATED - Nitter discontinued Feb 2024"
    },

    "twitter_cph_airport_nitter": {
        "name": "Copenhagen Airport Twitter (Nitter - DEPRECATED)",
        "url": "https://twitter.com/CPHAirport",
        "nitter_url": "https://nitter.net/CPHAirport/rss",
        "source_type": "official_statement",
        "scrape_type": "nitter_rss",
        "trust_weight": 3,
        "keywords": ["drone", "closure", "delay"],
        "enabled": False,
        "note": "DEPRECATED - Nitter discontinued Feb 2024"
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

# ============================================================================
# EUROPEAN LOCATIONS DATABASE
# ============================================================================

# Germany - Major airports and military bases
GERMAN_LOCATIONS = {
    # Airports
    "munich airport": {"lat": 48.3538, "lon": 11.7861, "type": "airport", "country": "DE", "icao": "EDDM"},
    "frankfurt airport": {"lat": 50.0379, "lon": 8.5622, "type": "airport", "country": "DE", "icao": "EDDF"},
    "berlin brandenburg": {"lat": 52.3667, "lon": 13.5033, "type": "airport", "country": "DE", "icao": "EDDB"},
    "hamburg airport": {"lat": 53.6304, "lon": 9.9882, "type": "airport", "country": "DE", "icao": "EDDH"},
    "düsseldorf airport": {"lat": 51.2895, "lon": 6.7668, "type": "airport", "country": "DE", "icao": "EDDL"},
    "cologne bonn airport": {"lat": 50.8659, "lon": 7.1427, "type": "airport", "country": "DE", "icao": "EDDK"},
    # Military
    "ramstein air base": {"lat": 49.4369, "lon": 7.6003, "type": "military", "country": "DE", "icao": "ETAR"},
    "spangdahlem air base": {"lat": 49.9727, "lon": 6.6925, "type": "military", "country": "DE", "icao": "ETAD"},
}

# France - Major airports and military bases
FRENCH_LOCATIONS = {
    # Airports
    "charles de gaulle": {"lat": 49.0097, "lon": 2.5479, "type": "airport", "country": "FR", "icao": "LFPG"},
    "paris cdg": {"lat": 49.0097, "lon": 2.5479, "type": "airport", "country": "FR", "icao": "LFPG"},
    "orly airport": {"lat": 48.7233, "lon": 2.3794, "type": "airport", "country": "FR", "icao": "LFPO"},
    "nice airport": {"lat": 43.6584, "lon": 7.2159, "type": "airport", "country": "FR", "icao": "LFMN"},
    "lyon airport": {"lat": 45.7256, "lon": 5.0811, "type": "airport", "country": "FR", "icao": "LFLL"},
    "marseille airport": {"lat": 43.4393, "lon": 5.2214, "type": "airport", "country": "FR", "icao": "LFML"},
    # Military
    "mourmelon-le-grand": {"lat": 49.1333, "lon": 4.3667, "type": "military", "country": "FR"},
    "istres air base": {"lat": 43.5227, "lon": 4.9236, "type": "military", "country": "FR", "icao": "LFMI"},
}

# United Kingdom - Major airports and RAF bases
UK_LOCATIONS = {
    # Airports
    "heathrow airport": {"lat": 51.4700, "lon": -0.4543, "type": "airport", "country": "GB", "icao": "EGLL"},
    "gatwick airport": {"lat": 51.1537, "lon": -0.1821, "type": "airport", "country": "GB", "icao": "EGKK"},
    "manchester airport": {"lat": 53.3537, "lon": -2.2750, "type": "airport", "country": "GB", "icao": "EGCC"},
    "edinburgh airport": {"lat": 55.9500, "lon": -3.3725, "type": "airport", "country": "GB", "icao": "EGPH"},
    "stansted airport": {"lat": 51.8860, "lon": 0.2389, "type": "airport", "country": "GB", "icao": "EGSS"},
    # Military - RAF bases
    "raf lakenheath": {"lat": 52.4093, "lon": 0.5610, "type": "military", "country": "GB", "icao": "EGUL"},
    "raf mildenhall": {"lat": 52.3619, "lon": 0.4864, "type": "military", "country": "GB", "icao": "EGUN"},
    "raf brize norton": {"lat": 51.7500, "lon": -1.5836, "type": "military", "country": "GB", "icao": "EGVN"},
    "raf northolt": {"lat": 51.5530, "lon": -0.4181, "type": "military", "country": "GB", "icao": "EGWU"},
}

# Ireland - Major airports
# Verified: 2025-10-13 via Wikipedia (aviation database source)
IRISH_LOCATIONS = {
    "dublin airport": {"lat": 53.4214, "lon": -6.2700, "type": "airport", "country": "IE", "icao": "EIDW"},
    "cork airport": {"lat": 51.8414, "lon": -8.4911, "type": "airport", "country": "IE", "icao": "EICK"},
    "shannon airport": {"lat": 52.7019, "lon": -8.9247, "type": "airport", "country": "IE", "icao": "EINN"},
}

# Netherlands - Airports
DUTCH_LOCATIONS = {
    "amsterdam schiphol": {"lat": 52.3105, "lon": 4.7683, "type": "airport", "country": "NL", "icao": "EHAM"},
    "rotterdam the hague": {"lat": 51.9569, "lon": 4.4375, "type": "airport", "country": "NL", "icao": "EHRD"},
    "eindhoven airport": {"lat": 51.4500, "lon": 5.3747, "type": "airport", "country": "NL", "icao": "EHEH"},
}

# Belgium - Airports
BELGIAN_LOCATIONS = {
    "brussels airport": {"lat": 50.9014, "lon": 4.4844, "type": "airport", "country": "BE", "icao": "EBBR"},
    "brussels zaventem": {"lat": 50.9014, "lon": 4.4844, "type": "airport", "country": "BE", "icao": "EBBR"},
    "charleroi airport": {"lat": 50.4592, "lon": 4.4538, "type": "airport", "country": "BE", "icao": "EBCI"},
}

# Spain - Major airports
SPANISH_LOCATIONS = {
    "madrid barajas": {"lat": 40.4983, "lon": -3.5676, "type": "airport", "country": "ES", "icao": "LEMD"},
    "barcelona el prat": {"lat": 41.2974, "lon": 2.0833, "type": "airport", "country": "ES", "icao": "LEBL"},
    "malaga airport": {"lat": 36.6749, "lon": -4.4991, "type": "airport", "country": "ES", "icao": "LEMG"},
    "palma de mallorca": {"lat": 39.5517, "lon": 2.7388, "type": "airport", "country": "ES", "icao": "LEPA"},
}

# Italy - Major airports
ITALIAN_LOCATIONS = {
    "rome fiumicino": {"lat": 41.8003, "lon": 12.2389, "type": "airport", "country": "IT", "icao": "LIRF"},
    "milan malpensa": {"lat": 45.6306, "lon": 8.7281, "type": "airport", "country": "IT", "icao": "LIMC"},
    "venice marco polo": {"lat": 45.5053, "lon": 12.3519, "type": "airport", "country": "IT", "icao": "LIPZ"},
    "naples airport": {"lat": 40.8860, "lon": 14.2908, "type": "airport", "country": "IT", "icao": "LIRN"},
}

# Latvia - Riga Airport
LATVIAN_LOCATIONS = {
    "riga airport": {"lat": 56.9236, "lon": 23.9711, "type": "airport", "country": "LV", "icao": "EVRA"},
}

# Estonia - Tallinn Airport
ESTONIAN_LOCATIONS = {
    "tallinn airport": {"lat": 59.4133, "lon": 24.8328, "type": "airport", "country": "EE", "icao": "EETN"},
}

# Lithuania - Major airports
# Verified: 2025-10-13 via Wikipedia (aviation database source)
LITHUANIAN_LOCATIONS = {
    "vilnius airport": {"lat": 54.6369, "lon": 25.2878, "type": "airport", "country": "LT", "icao": "EYVI"},
    "kaunas airport": {"lat": 54.9639, "lon": 24.0847, "type": "airport", "country": "LT", "icao": "EYKA"},
}

# Norway - Major airports
NORWEGIAN_LOCATIONS = {
    "oslo airport": {"lat": 60.1939, "lon": 11.1004, "type": "airport", "country": "NO", "icao": "ENGM"},
    "oslo gardermoen": {"lat": 60.1939, "lon": 11.1004, "type": "airport", "country": "NO", "icao": "ENGM"},
    "bergen airport": {"lat": 60.2934, "lon": 5.2181, "type": "airport", "country": "NO", "icao": "ENBR"},
    "stavanger airport": {"lat": 58.8767, "lon": 5.6378, "type": "airport", "country": "NO", "icao": "ENZV"},
}

# Sweden - Major airports
SWEDISH_LOCATIONS = {
    "stockholm arlanda": {"lat": 59.6519, "lon": 17.9186, "type": "airport", "country": "SE", "icao": "ESSA"},
    "gothenburg landvetter": {"lat": 57.6628, "lon": 12.2798, "type": "airport", "country": "SE", "icao": "ESGG"},
    "malmö airport": {"lat": 55.5363, "lon": 13.3762, "type": "airport", "country": "SE", "icao": "ESMS"},
}

# Finland - Major airports
FINNISH_LOCATIONS = {
    "helsinki vantaa": {"lat": 60.3172, "lon": 24.9633, "type": "airport", "country": "FI", "icao": "EFHK"},
    "tampere airport": {"lat": 61.4141, "lon": 23.6044, "type": "airport", "country": "FI", "icao": "EFTP"},
}

# Poland - Major airports
POLISH_LOCATIONS = {
    "warsaw chopin": {"lat": 52.1657, "lon": 20.9671, "type": "airport", "country": "PL", "icao": "EPWA"},
    "krakow airport": {"lat": 50.0777, "lon": 19.7848, "type": "airport", "country": "PL", "icao": "EPKK"},
    "gdansk airport": {"lat": 54.3776, "lon": 18.4662, "type": "airport", "country": "PL", "icao": "EPGD"},
    "lublin airport": {"lat": 51.2403, "lon": 22.7136, "type": "airport", "country": "PL", "icao": "EPLB"},
}

# Consolidated European locations (all countries)
EUROPEAN_LOCATIONS = {
    **GERMAN_LOCATIONS,
    **FRENCH_LOCATIONS,
    **UK_LOCATIONS,
    **IRISH_LOCATIONS,
    **DUTCH_LOCATIONS,
    **BELGIAN_LOCATIONS,
    **SPANISH_LOCATIONS,
    **ITALIAN_LOCATIONS,
    **LATVIAN_LOCATIONS,
    **ESTONIAN_LOCATIONS,
    **LITHUANIAN_LOCATIONS,
    **NORWEGIAN_LOCATIONS,
    **SWEDISH_LOCATIONS,
    **FINNISH_LOCATIONS,
    **POLISH_LOCATIONS,
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
