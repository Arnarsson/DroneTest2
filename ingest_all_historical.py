#!/usr/bin/env python3
"""
Comprehensive historical drone incidents scraper for September 2025
Includes detailed article information and sources
"""
import json
import subprocess
from datetime import datetime

# API configuration
API_URL = "https://www.dronemap.cc/api/ingest"
TOKEN = "dw-secret-2025-nordic-drone-watch"

# Comprehensive list of all September 2025 drone incidents
incidents = [
    # DENMARK INCIDENTS
    {
        "title": "Copenhagen Airport - Major Drone Disruption",
        "narrative": "2-3 large drones observed in controlled airspace forcing nearly 4-hour suspension of flights from 8:46 PM to 12:30 AM. Police confirmed these were not hobby drones but large professional-grade UAVs. About 15 flights were diverted to Gothenburg, Malmö, and other airports. PM Frederiksen called it the 'most serious attack on Danish critical infrastructure to date'. NATO responded by increasing Baltic Sea presence.",
        "occurred_at": "2025-09-22T20:46:00Z",
        "first_seen_at": "2025-09-22T20:46:00Z",
        "last_seen_at": "2025-09-23T00:30:00Z",
        "lat": 55.6180,
        "lon": 12.6476,
        "asset_type": "airport",
        "status": "resolved",
        "evidence_score": 4,
        "country": "DK",
        "sources": [{
            "source_url": "https://www.bloomberg.com/news/articles/2025-09-25/drones-at-four-danish-airports",
            "source_type": "media",
            "source_quote": "Denmark's Prime Minister Mette Frederiksen said the country was a target of a serious attack on Danish critical infrastructure"
        }, {
            "source_url": "https://www.cnn.com/2025/09/23/europe/denmark-drones-hybrid-attacks-intl",
            "source_type": "media",
            "source_quote": "Police Commissioner Thorkild Fogde stated these were not amateur or hobby drones, but rather large drones with capable operators"
        }]
    },
    {
        "title": "Aalborg Airport - Second Danish Airport Closure",
        "narrative": "Drones observed over Aalborg Airport in northern Denmark forcing temporary closure. Part of wider systematic drone activity across multiple Danish airports within 48 hours of Copenhagen incident. Defense Minister Troels Lund Poulsen said it appeared a 'professional actor' was behind the 'systematic' flights.",
        "occurred_at": "2025-09-24T21:44:00Z",
        "lat": 57.0928,
        "lon": 9.8492,
        "asset_type": "airport",
        "status": "resolved",
        "evidence_score": 4,
        "country": "DK",
        "sources": [{
            "source_url": "https://www.cnn.com/2025/09/24/europe/denmark-aalborg-airport-closed-drones",
            "source_type": "media",
            "source_quote": "Drones close a Denmark airport for second time in a week"
        }]
    },
    {
        "title": "Billund Airport - Early Morning Drone Closure",
        "narrative": "Airport closed for one hour in early morning hours due to drone sightings. Police confirmed drones were gone by 03:00 CEST. Part of coordinated activity across multiple Danish airports.",
        "occurred_at": "2025-09-25T02:00:00Z",
        "lat": 55.7403,
        "lon": 9.1518,
        "asset_type": "airport",
        "status": "resolved",
        "evidence_score": 4,
        "country": "DK"
    },
    {
        "title": "Sønderborg Airport - Multiple Airport Coordination",
        "narrative": "Police received reports of drones near Sønderborg Airport as part of coordinated incidents affecting four Danish airports simultaneously. Authorities investigating as potential 'hybrid attack' on infrastructure.",
        "occurred_at": "2025-09-24T22:00:00Z",
        "lat": 54.9644,
        "lon": 9.7917,
        "asset_type": "airport",
        "status": "resolved",
        "evidence_score": 3,
        "country": "DK"
    },
    {
        "title": "Esbjerg Airport - Western Denmark Incident",
        "narrative": "Drone activity reported at Esbjerg Airport during multi-airport incident on September 24. Part of what authorities called systematic drone operations across Denmark.",
        "occurred_at": "2025-09-24T22:00:00Z",
        "lat": 55.5257,
        "lon": 8.5534,
        "asset_type": "airport",
        "status": "resolved",
        "evidence_score": 3,
        "country": "DK"
    },
    {
        "title": "Skrydstrup Air Base - Military Installation Targeted",
        "narrative": "Military air base reported drone observations during coordinated incidents. Defense Minister Troels Lund Poulsen stated it appeared a professional actor was behind the systematic flights, calling it a 'hybrid attack'.",
        "occurred_at": "2025-09-24T22:30:00Z",
        "lat": 55.2214,
        "lon": 9.2631,
        "asset_type": "military",
        "status": "resolved",
        "evidence_score": 4,
        "country": "DK",
        "sources": [{
            "source_url": "https://www.npr.org/2025/09/25/nx-s1-5553244/denmark-drones-airports",
            "source_type": "media",
            "source_quote": "Defense Minister Troels Lund Poulsen said it appeared a professional actor was behind the systematic flights"
        }]
    },
    {
        "title": "Kastrup Airbase - Brief Airspace Closure",
        "narrative": "Drone activity detected over Kastrup military airbase at 20:15 CEST leading to brief civil airspace closure. Part of ongoing drone incidents affecting Danish military installations.",
        "occurred_at": "2025-09-26T20:15:00Z",
        "lat": 55.6300,
        "lon": 12.6500,
        "asset_type": "military",
        "status": "resolved",
        "evidence_score": 4,
        "country": "DK"
    },
    {
        "title": "Karup Air Base - Denmark's Largest Military Base",
        "narrative": "1-2 drones observed around 8:15 PM both inside and outside the fence of Denmark's largest military base, which houses all armed forces helicopters, airspace surveillance, flight school and support functions. Midtjylland civilian airport sharing runways was briefly closed. NATO deployed FGS Hamburg air-defence frigate in response.",
        "occurred_at": "2025-09-27T20:15:00Z",
        "lat": 56.2975,
        "lon": 9.1247,
        "asset_type": "military",
        "status": "resolved",
        "evidence_score": 4,
        "country": "DK",
        "sources": [{
            "source_url": "https://www.aljazeera.com/news/2025/9/28/denmark-bans-drone-flights-after-latest-drone-sightings",
            "source_type": "media",
            "source_quote": "Police reported one to two drones were observed near and over the Karup military base, the country's biggest base"
        }, {
            "source_url": "https://denmark.news-pravda.com/en/denmark/2025/09/27/10591.html",
            "source_type": "media",
            "source_quote": "Danish police received drone alerts Friday night near Karup Air Base, the country's largest military site"
        }]
    },

    # NORWAY INCIDENT
    {
        "title": "Oslo Airport - Coordinated with Copenhagen",
        "narrative": "Oslo Airport experienced drone sightings on the same evening as Copenhagen, forcing temporary closure. Authorities believe this was part of coordinated activity across Nordic countries targeting critical infrastructure.",
        "occurred_at": "2025-09-22T21:00:00Z",
        "lat": 60.1939,
        "lon": 11.1004,
        "asset_type": "airport",
        "status": "resolved",
        "evidence_score": 4,
        "country": "NO",
        "sources": [{
            "source_url": "https://edition.cnn.com/2025/09/22/europe/copenhagen-oslo-airport-closed-drones",
            "source_type": "media",
            "source_quote": "Travel disruption for thousands after mystery drones closed two of Scandinavia's busiest airports"
        }]
    },

    # POLAND INCIDENTS
    {
        "title": "Warsaw Chopin Airport - Russian Drone Fleet Incursion",
        "narrative": "At least 19 military drones entered Polish airspace from Russia and Belarus at 11:30 PM CEST. Warsaw Chopin Airport closed for 2 hours. Polish and NATO forces scrambled jets, shooting down at least 8 drones. First time NATO engaged Russian assets since Ukraine war began. Poland invoked Article 4 of NATO treaty.",
        "occurred_at": "2025-09-09T23:30:00Z",
        "lat": 52.1657,
        "lon": 20.9670,
        "asset_type": "airport",
        "status": "resolved",
        "evidence_score": 4,
        "country": "PL",
        "sources": [{
            "source_url": "https://www.cnn.com/2025/09/09/europe/poland-scramble-jets-russian-drone-reports",
            "source_type": "media",
            "source_quote": "NATO shoots down Russian drones in Polish airspace, accusing Moscow of being absolutely reckless"
        }, {
            "source_url": "https://www.bloomberg.com/news/articles/2025-09-10/poland-scrambles-jets-shuts-warsaw-airport",
            "source_type": "media",
            "source_quote": "Poland Shoots Down Russian Drones and Slams Kremlin's Incursion"
        }]
    },
    {
        "title": "Warsaw Modlin Airport - Russian Drone Closure",
        "narrative": "Airport closed simultaneously with Warsaw Chopin during Russian drone incursion. Part of coordinated response to 19 military drones entering Polish airspace.",
        "occurred_at": "2025-09-09T23:30:00Z",
        "lat": 52.4511,
        "lon": 20.6517,
        "asset_type": "airport",
        "status": "resolved",
        "evidence_score": 4,
        "country": "PL"
    },
    {
        "title": "Rzeszów-Jasionka Airport - Eastern Poland Closure",
        "narrative": "Airport near Ukrainian border closed during Russian drone incursion. Strategic location for NATO operations supporting Ukraine.",
        "occurred_at": "2025-09-09T23:30:00Z",
        "lat": 50.1100,
        "lon": 22.0190,
        "asset_type": "airport",
        "status": "resolved",
        "evidence_score": 4,
        "country": "PL"
    },
    {
        "title": "Lublin Airport - Airspace Protection Closure",
        "narrative": "Airport closed as part of coordinated Polish response to Russian drone fleet entering airspace. Quick Reaction Alert triggered with multiple NATO air forces responding.",
        "occurred_at": "2025-09-09T23:30:00Z",
        "lat": 51.2403,
        "lon": 22.7136,
        "asset_type": "airport",
        "status": "resolved",
        "evidence_score": 4,
        "country": "PL"
    },

    # NETHERLANDS INCIDENT
    {
        "title": "Amsterdam Schiphol - Drone Near Miss with Transavia Jet",
        "narrative": "Drone came within 50 meters of a Transavia jet forcing runway closure on September 27. Part of wider pattern of drone incidents at major European airports. Schiphol joins Copenhagen, Aalborg, Frankfurt, Stockholm in recent drone disruptions.",
        "occurred_at": "2025-09-27T14:00:00Z",
        "lat": 52.3105,
        "lon": 4.7683,
        "asset_type": "airport",
        "status": "resolved",
        "evidence_score": 4,
        "country": "NL",
        "sources": [{
            "source_url": "https://airlive.net/incident/2025/09/27/breaking-a-drone-came-within-50-meters",
            "source_type": "media",
            "source_quote": "A drone came within 50 meters of a Transavia jet at Amsterdam Schiphol forcing runway closure"
        }]
    },

    # SWEDEN INCIDENT
    {
        "title": "Stockholm Arlanda - Drone Disruption",
        "narrative": "Stockholm Arlanda Airport experienced drone-related disruptions as part of wider pattern affecting major European airports in September 2025.",
        "occurred_at": "2025-09-25T18:00:00Z",
        "lat": 59.6519,
        "lon": 17.9186,
        "asset_type": "airport",
        "status": "resolved",
        "evidence_score": 3,
        "country": "SE"
    }
]

def ingest_incident(incident):
    """Send incident to API using curl"""
    # Prepare JSON data
    json_data = json.dumps(incident)

    # Use curl to send the request
    cmd = [
        'curl', '-X', 'POST', API_URL,
        '-H', f'Authorization: Bearer {TOKEN}',
        '-H', 'Content-Type: application/json',
        '-d', json_data,
        '-s'  # Silent mode
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            try:
                response = json.loads(result.stdout)
                if 'id' in response:
                    print(f"✅ {incident['title'][:50]}: {response['id']}")
                    return True
                else:
                    print(f"❌ {incident['title'][:50]}: {response.get('error', 'Unknown error')[:100]}")
                    return False
            except json.JSONDecodeError:
                print(f"❌ {incident['title'][:50]}: Invalid response")
                return False
        else:
            print(f"❌ {incident['title'][:50]}: Request failed")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ {incident['title'][:50]}: Timeout")
        return False
    except Exception as e:
        print(f"❌ {incident['title'][:50]}: {str(e)}")
        return False

def main():
    print("\n" + "="*70)
    print("📚 COMPREHENSIVE HISTORICAL DRONE INCIDENTS INGESTION")
    print("September 2025 - Nordic & European Incidents")
    print("="*70 + "\n")

    # Sort incidents by date for chronological ingestion
    incidents.sort(key=lambda x: x['occurred_at'])

    success_count = 0
    error_count = 0

    print(f"📤 Ingesting {len(incidents)} incidents...\n")

    for incident in incidents:
        if ingest_incident(incident):
            success_count += 1
        else:
            error_count += 1

    print("\n" + "="*70)
    print("📊 Summary")
    print("="*70)
    print(f"✅ Success: {success_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📍 Countries: {', '.join(sorted(set(i['country'] for i in incidents)))}")
    print(f"🎯 Asset types: {', '.join(sorted(set(i['asset_type'] for i in incidents)))}")
    print(f"📅 Date range: Sep 9-27, 2025")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()