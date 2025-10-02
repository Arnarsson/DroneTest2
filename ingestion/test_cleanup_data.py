#!/usr/bin/env python3
"""
Test script to demonstrate OpenAI cleanup on mock incident data.
"""

import json
import os
from datetime import datetime

from openai_client import OpenAIClient, OpenAIClientError

# Mock data from user
MOCK_DATA = [
    {
        "id": "24a89a45-72da-49c3-9366-c82c2135fe5b",
        "title": "Udenlandske soldater skal hjælpe Danmark efter dronehændelser",
        "narrative": "Starter etterforskning etter droneobservasjon i Nordsjøen Politiet har startet etterforskning etter en droneobservasjon ved Sleipner-feltet i Nordsjøen mandag kveld. Det var ved Sleipner-feltet vest for Stavanger at det ble gjort en mulig droneobservasjon mandag. Nå har politiet startet etterforskning. Foto: Ole Berg-Rusten Håkon Jonassen Norheim – Journalist Journalist Publisert 01.10.2025, kl. 10.02 Oppdatert 01.10.2025, kl. 10.13 – Politiet fikk melding om droneobservasjon ved Sleipner-feltet",
        "occurred_at": "2025-10-01T05:03:00+00:00",
        "first_seen_at": "2025-10-01T05:03:00+00:00",
        "last_seen_at": "2025-10-01T10:31:53+00:00",
        "asset_type": "military",
        "status": "active",
        "evidence_score": 3,
        "country": "DK",
        "lat": 55.6761,
        "lon": 12.5683,
        "sources": []
    },
    {
        "id": "62b3a8a5-771b-428d-bd36-795cb81c9e58",
        "title": "Eksplosiv vækst: Droneangreb har fået mange til at melde sig",
        "narrative": "Eksplosiv vækst: Droneangreb har fået mange til at melde sig Hjemmeværnets styrke af soldater vokser - især efter sidste uges hybridangreb med droner. Men der er brug for endnu flere, siger lektor ved Forsvarsakademiet. Foto: Liselotte Sabroe/Ritzau Scanpix Er du klar til at beskytte Danmark i tilfælde af krig? Det spørgsmål ser ud til at have rumsteret i flere danskeres sind efter sidste uges droneangreb, der lammede flytrafikken i København og Jylland. I hvert fald er tilmeldingen til Hjemmevæ",
        "occurred_at": "2025-10-01T04:00:00+00:00",
        "first_seen_at": "2025-10-01T04:00:00+00:00",
        "last_seen_at": "2025-10-01T08:30:00+00:00",
        "asset_type": "airport",
        "status": "active",
        "evidence_score": 3,
        "country": "DK",
        "lat": 55.618,
        "lon": 12.6476,
        "sources": []
    },
    {
        "id": "4d918254-cbca-4248-ac2b-51bcf9d05d12",
        "title": "Skib med mulig forbindelse til dronesagen efterforskes i Frankrig",
        "narrative": "play-circle play-circle Læs op USA har drone-værn i København under topmøde USA støtter Danmark med \" anti-drone kapabiliteter\" i forbindelse med ugens EU-topmøde i København. Det skriver Forsvarsministeriet på X. - Vi er glade for og taknemmelige over, at USA også støtter Danmark med antidrone kapabiliteter i forbindelse med det kommende topmøde. - Den amerikanske støtte er et udtryk for det tætte transatlantiske samarbejde, som også står stærkt i håndteringen af hybride angreb, skriver ministe",
        "occurred_at": "2025-09-30T13:37:00+00:00",
        "first_seen_at": "2025-09-30T13:37:00+00:00",
        "last_seen_at": "2025-09-30T19:20:35+00:00",
        "asset_type": "airport",
        "status": "active",
        "evidence_score": 3,
        "country": "DK",
        "lat": 55.618,
        "lon": 12.649600000000001,
        "sources": []
    },
    {
        "id": "d66a477a-5446-4d50-8c54-718ec3e20504",
        "title": "Forsvaret bekrefter: Økning av droneobservasjoner ved militære anlegg",
        "narrative": "Forsvaret orientert om mulig droneobservasjon ved Sleipner-plattformen Forsvaret er orientert om gårsdagens droneobservasjon i Nordsjøen. Men har foreløpig ikke noen aktiv rolle i det. Det var ved Sleipner-plattformen vest for Stavanger at den mulige droneobservasjonen ble gjort. Foto: Dag Tore Anfinsen / Statoil Håkon Jonassen Norheim – Journalist Journalist Even Hye Tytlandsvik Barka – Journalist Journalist Simon Elias Vik Bogen – Journalist Journalist Vi rapporterer fra Stavanger Publisert 30",
        "occurred_at": "2025-09-30T10:41:51+00:00",
        "first_seen_at": "2025-09-30T10:41:51+00:00",
        "last_seen_at": "2025-09-30T21:38:44+00:00",
        "asset_type": "military",
        "status": "active",
        "evidence_score": 3,
        "country": "DK",
        "lat": 55.6761,
        "lon": 12.570300000000001,
        "sources": []
    },
    {
        "id": "1899d29f-81b7-4724-95f2-53e19b57ce78",
        "title": "France, Sweden send anti-drone units to Denmark to secure EU summit",
        "narrative": "PARIS — France sent a military anti-drone unit to Denmark, and Sweden is planning to do the same, as the allies seek to help secure an informal European Union summit in Copenhagen this week against aerial threats, following recent flights of unidentified drones in Danish airspace. The French military has deployed a team of 35 personnel with a Fennec light helicopter and “active anti-drone capabilities,” the country’s Armed Forces Ministry said in a statement Monday. Meanwhile, Sweden will send a",
        "occurred_at": "2025-09-29T15:14:50+00:00",
        "first_seen_at": "2025-09-29T15:14:50+00:00",
        "last_seen_at": "2025-09-29T18:56:39+00:00",
        "asset_type": "airport",
        "status": "active",
        "evidence_score": 3,
        "country": "DK",
        "lat": 55.619902113032595,
        "lon": 12.648218033988751,
        "sources": []
    },
    {
        "id": "18e9d6c6-5c6e-4816-9dbd-787fcbd20537",
        "title": "EU vows haste in ‘drone wall’ plan for eastern borders",
        "narrative": "BERLIN — The European Union has jump-started the development of a so-called “drone wall” to protect European skies against incursions by unmanned aerial vehicles from Russia, alongside a broader set of measures designed to protect the eastern flank of the continent. The package of proposed measures will be called Eastern Flank Watch and was announced by EU Commission President Ursula von der Leyen in a landmark speech earlier this month . Details emerged on Friday, with the EU commissioner for d",
        "occurred_at": "2025-09-29T10:38:38+00:00",
        "first_seen_at": "2025-09-29T10:38:38+00:00",
        "last_seen_at": "2025-09-29T18:19:00+00:00",
        "asset_type": "military",
        "status": "active",
        "evidence_score": 3,
        "country": "DK",
        "lat": 55.67751421356237,
        "lon": 12.569714213562374,
        "sources": []
    },
    {
        "id": "f79f8e58-9dd7-4dba-aec1-b81671905e51",
        "title": "Karup Air Base - Denmark's Largest Military Base",
        "narrative": "1-2 drones observed around 8:15 PM both inside and outside the fence of Denmark's largest military base, which houses all armed forces helicopters, airspace surveillance, flight school and support functions. Midtjylland civilian airport sharing runways was briefly closed. NATO deployed FGS Hamburg air-defence frigate in response.",
        "occurred_at": "2025-09-27T20:15:00+00:00",
        "first_seen_at": "2025-09-27T20:15:00+00:00",
        "last_seen_at": "2025-09-27T20:15:00+00:00",
        "asset_type": "military",
        "status": "resolved",
        "evidence_score": 4,
        "country": "DK",
        "lat": 56.2975,
        "lon": 9.1247,
        "sources": []
    },
    {
        "id": "5028062c-78c7-4c6c-a131-67e58fe9f23f",
        "title": "Amsterdam Schiphol - Drone Near Miss with Transavia Jet",
        "narrative": "Drone came within 50 meters of a Transavia jet forcing runway closure on September 27. Part of wider pattern of drone incidents at major European airports. Schiphol joins Copenhagen, Aalborg, Frankfurt, Stockholm in recent drone disruptions.",
        "occurred_at": "2025-09-27T14:00:00+00:00",
        "first_seen_at": "2025-09-27T14:00:00+00:00",
        "last_seen_at": "2025-09-27T14:00:00+00:00",
        "asset_type": "airport",
        "status": "resolved",
        "evidence_score": 4,
        "country": "NL",
        "lat": 52.3105,
        "lon": 4.7683,
        "sources": []
    },
    {
        "id": "865506b1-4a5c-4c8e-a7b2-7d60e0d8581b",
        "title": "Kastrup Airbase - Brief Airspace Closure",
        "narrative": "Drone activity detected over Kastrup military airbase at 20:15 CEST leading to brief civil airspace closure. Part of ongoing drone incidents affecting Danish military installations.",
        "occurred_at": "2025-09-26T20:15:00+00:00",
        "first_seen_at": "2025-09-26T20:15:00+00:00",
        "last_seen_at": "2025-09-26T20:15:00+00:00",
        "asset_type": "military",
        "status": "resolved",
        "evidence_score": 4,
        "country": "DK",
        "lat": 55.63,
        "lon": 12.65,
        "sources": []
    },
    {
        "id": "1e7c3223-9429-43bc-80ed-0f2f84bdf82d",
        "title": "European navies test new drone tech for undersea operations",
        "narrative": "SESIMBRA, Portugal — An hour from Portugal’s capital, Lisbon, on a clear sunny day in late September, a large, penguin-like robot peeks above the sea surface. It circles a Portuguese Navy ship from a distance, hardly visible to the human eye, concealed by the deep blue waters of the Atlantic ocean. The system is the Greyshark from Germany’s EuroAtlas, an autonomous underwater vehicle measuring 6.5 meters in length and weighing as much as a delivery van. It is one of the naval drones the German N",
        "occurred_at": "2025-09-26T11:09:17+00:00",
        "first_seen_at": "2025-09-26T11:09:17+00:00",
        "last_seen_at": "2025-09-26T11:09:17+00:00",
        "asset_type": "military",
        "status": "active",
        "evidence_score": 3,
        "country": "DK",
        "lat": 55.6781,
        "lon": 12.5683,
        "sources": []
    },
    {
        "id": "9c8f7692-763d-42b3-ba50-95cd620bf031",
        "title": "Stockholm Arlanda - Drone Disruption",
        "narrative": "Stockholm Arlanda Airport experienced drone-related disruptions as part of wider pattern affecting major European airports in September 2025.",
        "occurred_at": "2025-09-25T18:00:00+00:00",
        "first_seen_at": "2025-09-25T18:00:00+00:00",
        "last_seen_at": "2025-09-25T18:00:00+00:00",
        "asset_type": "airport",
        "status": "resolved",
        "evidence_score": 3,
        "country": "SE",
        "lat": 59.6519,
        "lon": 17.9186,
        "sources": []
    },
    {
        "id": "16c6d1af-8727-4e1c-8e85-8bae4d3e9823",
        "title": "Ukraine navy, a battle-tested force, plays enemy in NATO drone drill",
        "narrative": "TROIA, Portugal — Representatives from the Ukrainian navy participated in NATO’s largest unmanned maritime systems exercise this month, simulating the opposing force to test the capabilities of two dozen allied countries in scenarios inspired by frontline action. Ukraine was one of 24 countries that took part in the Portugal-led military exercise, REPMUS 2025, from Sept. 1-26, dedicated to testing hundreds of autonomous systems for naval applications. Captain Valter de Bulha Almeida of the Portu",
        "occurred_at": "2025-09-25T15:43:43+00:00",
        "first_seen_at": "2025-09-25T15:43:43+00:00",
        "last_seen_at": "2025-09-25T22:06:00+00:00",
        "asset_type": "military",
        "status": "active",
        "evidence_score": 3,
        "country": "DK",
        "lat": 55.67751421356237,
        "lon": 12.566885786437627,
        "sources": []
    },
    {
        "id": "6bd476b0-2ca9-4f8d-a4bf-f6d84dc03989",
        "title": "Billund Airport - Early Morning Drone Closure",
        "narrative": "Airport closed for one hour in early morning hours due to drone sightings. Police confirmed drones were gone by 03:00 CEST. Part of coordinated activity across multiple Danish airports.",
        "occurred_at": "2025-09-25T02:00:00+00:00",
        "first_seen_at": "2025-09-25T02:00:00+00:00",
        "last_seen_at": "2025-09-25T02:00:00+00:00",
        "asset_type": "airport",
        "status": "resolved",
        "evidence_score": 4,
        "country": "DK",
        "lat": 55.7403,
        "lon": 9.1518,
        "sources": []
    },
    {
        "id": "4d16637c-ee52-42a1-986e-03ead51fd37f",
        "title": "Skrydstrup Air Base - Military Installation Targeted",
        "narrative": "Military air base reported drone observations during coordinated incidents. Defense Minister Troels Lund Poulsen stated it appeared a professional actor was behind the systematic flights, calling it a 'hybrid attack'.",
        "occurred_at": "2025-09-24T22:30:00+00:00",
        "first_seen_at": "2025-09-24T22:30:00+00:00",
        "last_seen_at": "2025-09-24T22:30:00+00:00",
        "asset_type": "military",
        "status": "resolved",
        "evidence_score": 4,
        "country": "DK",
        "lat": 55.2214,
        "lon": 9.2631,
        "sources": []
    },
    {
        "id": "beb3df14-af7d-4184-b96f-1c792a2322f8",
        "title": "Sønderborg Airport - Multiple Airport Coordination",
        "narrative": "Police received reports of drones near Sønderborg Airport as part of coordinated incidents affecting four Danish airports simultaneously. Authorities investigating as potential 'hybrid attack' on infrastructure.",
        "occurred_at": "2025-09-24T22:00:00+00:00",
        "first_seen_at": "2025-09-24T22:00:00+00:00",
        "last_seen_at": "2025-09-24T22:00:00+00:00",
        "asset_type": "airport",
        "status": "resolved",
        "evidence_score": 3,
        "country": "DK",
        "lat": 54.9644,
        "lon": 9.7917,
        "sources": []
    },
    {
        "id": "73e367aa-8c31-4de3-950e-1a4077bebb6a",
        "title": "Esbjerg Airport - Western Denmark Incident",
        "narrative": "Drone activity reported at Esbjerg Airport during multi-airport incident on September 24. Part of what authorities called systematic drone operations across Denmark.",
        "occurred_at": "2025-09-24T22:00:00+00:00",
        "first_seen_at": "2025-09-24T22:00:00+00:00",
        "last_seen_at": "2025-09-24T22:00:00+00:00",
        "asset_type": "airport",
        "status": "resolved",
        "evidence_score": 3,
        "country": "DK",
        "lat": 55.5257,
        "lon": 8.5534,
        "sources": []
    },
    {
        "id": "df02e3be-851e-412c-9969-fda497ffaa70",
        "title": "Aalborg Airport - Second Danish Airport Closure",
        "narrative": "Drones observed over Aalborg Airport in northern Denmark forcing temporary closure. Part of wider systematic drone activity across multiple Danish airports within 48 hours of Copenhagen incident. Defense Minister Troels Lund Poulsen said it appeared a 'professional actor' was behind the 'systematic' flights.",
        "occurred_at": "2025-09-24T21:44:00+00:00",
        "first_seen_at": "2025-09-24T21:44:00+00:00",
        "last_seen_at": "2025-09-24T21:44:00+00:00",
        "asset_type": "airport",
        "status": "resolved",
        "evidence_score": 4,
        "country": "DK",
        "lat": 57.0928,
        "lon": 9.8492,
        "sources": []
    },
    {
        "id": "d8a3e8c5-f5be-4170-91b2-56772a149b0f",
        "title": "F-15Es Tried To Shoot Down Iranian Kamikaze Drones With Laser Guided Bombs",
        "narrative": "F-15 Depicted Launching LongShot Air-To-Air Missile Carrier Drone In New Renderings General Atomics has told us that LongShot, which can be launched by bombers and cargo planes, too, is not intended to be reusable operationally. By Joseph Trevithick Published Sep 24, 2025 5:20 PM EDT 0 General Atomics The TWZ Newsletter Weekly insights and analysis on the latest developments in military technology, strategy, and foreign policy. Email address Sign Up Thank you! Terms of Service and Privacy Policy",
        "occurred_at": "2025-09-24T00:24:15+00:00",
        "first_seen_at": "2025-09-24T00:24:15+00:00",
        "last_seen_at": "2025-09-24T21:20:32+00:00",
        "asset_type": "military",
        "status": "active",
        "evidence_score": 3,
        "country": "DK",
        "lat": 55.6761,
        "lon": 12.5663,
        "sources": []
    },
    {
        "id": "5e8468e7-66b7-461e-a0bc-a24fc16327f4",
        "title": "Denmark Says Drone Incursions Were A Deliberate “Attack”",
        "narrative": "Denmark Says Drone Incursions Were A Deliberate “Attack” The Danish prime minister has described the incident as the most serious attack on the country’s critical infrastructure to date. By Thomas Newdick Published Sep 23, 2025 11:58 AM EDT 0 Photo by STEVEN KNAP/Ritzau Scanpix/AFP via Getty Images The TWZ Newsletter Weekly insights and analysis on the latest developments in military technology, strategy, and foreign policy. Email address Sign Up Thank you! Terms of Service and Privacy Policy De",
        "occurred_at": "2025-09-23T15:58:03+00:00",
        "first_seen_at": "2025-09-23T15:58:03+00:00",
        "last_seen_at": "2025-09-23T15:58:03+00:00",
        "asset_type": "airport",
        "status": "active",
        "evidence_score": 3,
        "country": "DK",
        "lat": 55.61917557050459,
        "lon": 12.64598196601125,
        "sources": []
    },
    {
        "id": "e47623c6-5d90-4190-bce2-af1b99786cc5",
        "title": "Oslo Airport - Coordinated with Copenhagen",
        "narrative": "Oslo Airport experienced drone sightings on the same evening as Copenhagen, forcing temporary closure. Authorities believe this was part of coordinated activity across Nordic countries targeting critical infrastructure.",
        "occurred_at": "2025-09-22T21:00:00+00:00",
        "first_seen_at": "2025-09-22T21:00:00+00:00",
        "last_seen_at": "2025-09-22T21:00:00+00:00",
        "asset_type": "airport",
        "status": "resolved",
        "evidence_score": 4,
        "country": "NO",
        "lat": 60.1939,
        "lon": 11.1004,
        "sources": []
    },
    {
        "id": "0e7a4198-4e93-4cf7-ad2e-9b464b0f7813",
        "title": "Copenhagen Airport - Major Drone Disruption",
        "narrative": "2-3 large drones observed in controlled airspace forcing nearly 4-hour suspension of flights from 8:46 PM to 12:30 AM. Police confirmed these were not hobby drones but large professional-grade UAVs. About 15 flights were diverted to Gothenburg, Malmö, and other airports. PM Frederiksen called it the 'most serious attack on Danish critical infrastructure to date'. NATO responded by increasing Baltic Sea presence.",
        "occurred_at": "2025-09-22T20:46:00+00:00",
        "first_seen_at": "2025-09-22T20:46:00+00:00",
        "last_seen_at": "2025-09-23T00:30:00+00:00",
        "asset_type": "airport",
        "status": "resolved",
        "evidence_score": 4,
        "country": "DK",
        "lat": 55.616824429495416,
        "lon": 12.64598196601125,
        "sources": []
    },
    {
        "id": "20a126bd-0275-4a3a-8049-c90a307dcb8a",
        "title": "Ukrainian Drones Strike Russia’s Rare Be-12 Flying Boats",
        "narrative": "Anduril’s Fury Will Take Off For The First Time At The Touch Of A Button A semi-autonomous YFQ-44A Collaborative Combat Drone's maiden flight is part of Anduril's strategy to get to an operational capability faster. By Joseph Trevithick Updated Sep 22, 2025 6:53 PM EDT 0 Courtesy photo via USAF The TWZ Newsletter Weekly insights and analysis on the latest developments in military technology, strategy, and foreign policy. Email address Sign Up Thank you! Terms of Service and Privacy Policy When A",
        "occurred_at": "2025-09-22T19:40:59+00:00",
        "first_seen_at": "2025-09-22T19:40:59+00:00",
        "last_seen_at": "2025-09-22T22:53:04+00:00",
        "asset_type": "military",
        "status": "active",
        "evidence_score": 3,
        "country": "DK",
        "lat": 55.67468578643763,
        "lon": 12.566885786437627,
        "sources": []
    },
    {
        "id": "e0946d7b-bde6-47ff-ab0a-df76e4e6fcba",
        "title": "Skunk Works Unveils Vectis Air Combat Drone That Puts A Premium On Stealth",
        "narrative": "Skunk Works Unveils Vectis Air Combat Drone That Puts A Premium On Stealth Lockheed's new Collaborative Combat Aircraft, targeted to fly in two years, reflects a higher-end approach compared to types the USAF has selected so far. By Joseph Trevithick Published Sep 21, 2025 12:01 AM EDT 0 Lockheed Martin The TWZ Newsletter Weekly insights and analysis on the latest developments in military technology, strategy, and foreign policy. Email address Sign Up Thank you! Terms of Service and Privacy Poli",
        "occurred_at": "2025-09-21T04:01:05+00:00",
        "first_seen_at": "2025-09-21T04:01:05+00:00",
        "last_seen_at": "2025-09-21T04:01:05+00:00",
        "asset_type": "military",
        "status": "active",
        "evidence_score": 3,
        "country": "DK",
        "lat": 55.674099999999996,
        "lon": 12.5683,
        "sources": []
    },
    {
        "id": "44c7bdbe-2baf-4654-9a15-371d0732739a",
        "title": "Warsaw Chopin Airport - Russian Drone Fleet Incursion",
        "narrative": "At least 19 military drones entered Polish airspace from Russia and Belarus at 11:30 PM CEST. Warsaw Chopin Airport closed for 2 hours. Polish and NATO forces scrambled jets, shooting down at least 8 drones. First time NATO engaged Russian assets since Ukraine war began. Poland invoked Article 4 of NATO treaty.",
        "occurred_at": "2025-09-09T23:30:00+00:00",
        "first_seen_at": "2025-09-09T23:30:00+00:00",
        "last_seen_at": "2025-09-09T23:30:00+00:00",
        "asset_type": "airport",
        "status": "resolved",
        "evidence_score": 4,
        "country": "PL",
        "lat": 52.1657,
        "lon": 20.967,
        "sources": []
    },
    {
        "id": "acbe7aab-c951-407f-9b15-08377159f567",
        "title": "Warsaw Modlin Airport - Russian Drone Closure",
        "narrative": "Airport closed simultaneously with Warsaw Chopin during Russian drone incursion. Part of coordinated response to 19 military drones entering Polish airspace.",
        "occurred_at": "2025-09-09T23:30:00+00:00",
        "first_seen_at": "2025-09-09T23:30:00+00:00",
        "last_seen_at": "2025-09-09T23:30:00+00:00",
        "asset_type": "airport",
        "status": "resolved",
        "evidence_score": 4,
        "country": "PL",
        "lat": 52.4511,
        "lon": 20.6517,
        "sources": []
    },
    {
        "id": "520417ea-3485-4d25-9892-9e52a465d0f0",
        "title": "Rzeszów-Jasionka Airport - Eastern Poland Closure",
        "narrative": "Airport near Ukrainian border closed during Russian drone incursion. Strategic location for NATO operations supporting Ukraine.",
        "occurred_at": "2025-09-09T23:30:00+00:00",
        "first_seen_at": "2025-09-09T23:30:00+00:00",
        "last_seen_at": "2025-09-09T23:30:00+00:00",
        "asset_type": "airport",
        "status": "resolved",
        "evidence_score": 4,
        "country": "PL",
        "lat": 50.11,
        "lon": 22.019,
        "sources": []
    },
    {
        "id": "8f2d3251-44ac-4687-8730-c3647d7de5d1",
        "title": "Lublin Airport - Airspace Protection Closure",
        "narrative": "Airport closed as part of coordinated Polish response to Russian drone fleet entering airspace. Quick Reaction Alert triggered with multiple NATO air forces responding.",
        "occurred_at": "2025-09-09T23:30:00+00:00",
        "first_seen_at": "2025-09-09T23:30:00+00:00",
        "last_seen_at": "2025-09-09T23:30:00+00:00",
        "asset_type": "airport",
        "status": "resolved",
        "evidence_score": 4,
        "country": "PL",
        "lat": 51.2403,
        "lon": 22.7136,
        "sources": []
    }
]


def test_cleanup():
    """Test OpenAI cleanup on mock incident data."""

    # Check if API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("[ERROR] OPENAI_API_KEY not set. Set it to test cleanup functionality.")
        print("   Example: export OPENAI_API_KEY='your-key-here'")
        return

    try:
        client = OpenAIClient()
        print("[OK] OpenAI client initialized successfully")
    except Exception as e:
        print(f"[ERROR] Failed to initialize OpenAI client: {e}")
        return

    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    results_file = f"cleanup_results_{timestamp}.txt"

    print(f"\n🧪 Testing cleanup on {len(MOCK_DATA)} mock incidents...")
    print("=" * 80)

    # Open file for writing results
    with open(results_file, "w", encoding="utf-8") as f:
        f.write("OpenAI Text Cleanup Results\n")
        f.write("=" * 50 + "\n\n")

    for i, incident in enumerate(MOCK_DATA, 1):
        print(f"\n📰 Incident {i}: {incident['title']}")
        print("-" * 60)

        original_narrative = incident['narrative']
        print(f"📝 ORIGINAL ({len(original_narrative)} chars):")
        print(f"   {original_narrative}")

        try:
            cleaned_narrative = client.cleanup_text(original_narrative)
            print(f"\n✨ CLEANED ({len(cleaned_narrative)} chars):")
            print(f"   {cleaned_narrative}")

            # Show improvement
            removed_chars = len(original_narrative) - len(cleaned_narrative)
            if removed_chars > 0:
                print(f"   🗑️  Removed {removed_chars} characters of noise")
            elif removed_chars < 0:
                print(f"   📈 Added {abs(removed_chars)} characters")
            else:
                print(f"   ⚖️  No length change")

            # Write to file
            with open(results_file, "a", encoding="utf-8") as f:
                f.write(f"INCIDENT {i}: {incident['title']}\n")
                f.write("-" * 60 + "\n")
                f.write(f"ORIGINAL ({len(original_narrative)} chars):\n")
                f.write(f"{original_narrative}\n\n")
                f.write(f"CLEANED ({len(cleaned_narrative)} chars):\n")
                f.write(f"{cleaned_narrative}\n\n")
                f.write(
                    f"IMPROVEMENT: {'Removed' if removed_chars > 0 else 'Added' if removed_chars < 0 else 'No change'} {abs(removed_chars) if removed_chars != 0 else ''} characters\n")
                f.write("=" * 80 + "\n\n")

        except OpenAIClientError as e:
            print(f"❌ Cleanup failed: {e}")
            with open(results_file, "a", encoding="utf-8") as f:
                f.write(f"INCIDENT {i}: {incident['title']}\n")
                f.write(f"ERROR: Cleanup failed - {e}\n")
                f.write("=" * 80 + "\n\n")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            with open(results_file, "a", encoding="utf-8") as f:
                f.write(f"INCIDENT {i}: {incident['title']}\n")
                f.write(f"ERROR: Unexpected error - {e}\n")
                f.write("=" * 80 + "\n\n")

        print()

    print(f"\n📄 Results saved to: {results_file}")


if __name__ == "__main__":
    test_cleanup()
