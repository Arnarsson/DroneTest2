#!/usr/bin/env python3
"""
Non-Incident Filter
Filters out news about drone regulations, bans, and advisories that aren't actual incidents.
"""

from typing import Dict, Tuple, List
import re


class NonIncidentFilter:
    """Detects and filters news about regulations/bans rather than actual incidents"""

    # Keywords indicating regulatory/advisory news (not incidents)
    REGULATORY_KEYWORDS = {
        # English
        'ban', 'banned', 'restriction', 'restricted', 'prohibit', 'prohibited',
        'regulation', 'rule', 'rules', 'law', 'legislation', 'advisory', 'warning',
        'no-fly zone', 'temporary flight restriction', 'tfr', 'notam',
        'upcoming', 'planned', 'will be', 'going to be', 'future',
        'harmonized', 'harmonize', 'standardize', 'framework', 'guideline', 'guidelines',
        'issued', 'issues', 'announces', 'announced', 'announcement',
        'proposes', 'proposed', 'proposal', 'introduces', 'introduced',

        # Danish
        'forbud', 'forbudt', 'forbyder', 'restriktion', 'begrænsning',
        'regel', 'regler', 'lov', 'lovgivning', 'advarsel', 'vejledning',
        'kommende', 'planlagt', 'vil blive', 'skal være',
        'annoncerer', 'annonceret', 'foreslår', 'foreslået',

        # Norwegian
        'forbud', 'forbudt', 'restriksjon', 'begrensning', 'regel', 'regler',
        'annonserer', 'annonsert', 'foreslår', 'foreslått',

        # Swedish
        'förbud', 'förbjudet', 'restriktion', 'begränsning', 'regel', 'regler',
        'utfärdar', 'utfärdad', 'föreslår', 'föreslagen',

        # German
        'verbot', 'verboten', 'beschränkung', 'einschränkung', 'vorschrift',
        'ankündigt', 'angekündigt', 'vorschlägt', 'vorgeschlagen',

        # French
        'interdit', 'interdiction', 'restriction', 'règlement', 'avertissement',
        'annonce', 'annoncé', 'propose', 'proposé',
    }

    # Simulation/Drill/Exercise keywords
    SIMULATION_KEYWORDS = {
        # English
        'simulation', 'simulated', 'exercise', 'drill', 'practice', 'training',
        'test flight', 'mock', 'demonstration', 'demo', 'rehearsal',

        # Danish
        'øvelse', 'træning', 'simulering', 'testflyvning', 'demonstration',
        'prøve', 'afprøvning', 'træningsøvelse',

        # Norwegian
        'øvelse', 'trening', 'simulering', 'testflyging', 'testflygning',
        'prøve', 'treningsøvelse',

        # Swedish
        'övning', 'träning', 'simulering', 'testflygning', 'demonstration',
        'prov', 'träningsövning',

        # Finnish
        'harjoitus', 'simulaatio', 'koulutus', 'testilento',
        'koe', 'harjoittelulento',

        # German
        'übung', 'simulation', 'test', 'demonstration', 'manöver',
        'probe', 'training', 'testflug',

        # French
        'exercice', 'simulation', 'entraînement', 'démonstration', 'manœuvre',
        'essai', 'vol test',

        # Dutch
        'oefening', 'simulatie', 'training', 'demonstratie',
        'proef', 'testvlucht',

        # Spanish
        'ejercicio', 'simulación', 'entrenamiento', 'demostración', 'maniobra',
        'prueba', 'vuelo de prueba',

        # Italian
        'esercitazione', 'simulazione', 'addestramento', 'dimostrazione',
        'prova', 'volo di prova',

        # Polish
        'ćwiczenia', 'symulacja', 'szkolenie', 'demonstracja',
        'próba', 'lot testowy',
    }

    # Phrases that indicate regulatory news
    REGULATORY_PHRASES = [
        # English
        r'drone\s+(ban|restriction|prohibition)',
        r'(new|temporary)\s+drone\s+(ban|restriction)',
        r'no-fly\s+zone',
        r'flight\s+restriction',
        r'airspace\s+(closure|restriction)',
        r'(ban|restrict)\s+drone',

        # Danish
        r'droneforbud',
        r'nye?\s+droneforbud',
        r'drone\s+forbud',
        r'giver\s+.*forbud',
        r'forbud\s+mod\s+drone',
        r'restriktion.*drone',

        # Norwegian
        r'droneforbud',
        r'forbud\s+mot\s+drone',

        # Swedish
        r'drönareförbud',
        r'förbud\s+mot\s+drönare',

        # German
        r'drohnenverbot',
        r'verbot.*drohne',

        # French
        r'interdiction.*drone',
        r'restriction.*drone',
    ]

    # Simulation/Exercise phrases
    SIMULATION_PHRASES = [
        # English
        r'military\s+exercise',
        r'airport\s+(drill|exercise)',
        r'test\s+of\s+.*drone.*system',
        r'planned\s+(exercise|drill)',
        r'training\s+(scenario|exercise)',
        r'counter.*drone.*(exercise|drill)',
        r'(practicing|rehearsing).*drone',
        r'simulated\s+(attack|incident)',

        # Danish/Norwegian/Swedish (similar)
        r'militær\s*øvelse',
        r'militær\s*övning',
        r'lufthavns\s*(øvelse|övning)',
        r'test.*drone.*system',
        r'planlagt\s*øvelse',
        r'trænings\s*øvelse',
        r'trenings\s*øvelse',

        # German
        r'militärische\s+übung',
        r'flughafen.*übung',
        r'test.*drohne.*system',
        r'geplante\s+übung',

        # French
        r'exercice\s+militaire',
        r'exercice.*aéroport',
        r'test.*système.*drone',
        r'exercice\s+planifié',

        # Dutch
        r'militaire\s+oefening',
        r'luchthaven.*oefening',

        # Spanish
        r'ejercicio\s+militar',
        r'ejercicio.*aeropuerto',

        # Italian
        r'esercitazione\s+militare',
        r'esercitazione.*aeroporto',

        # Polish
        r'ćwiczenia\s+wojskowe',
        r'ćwiczenia.*lotnisko',
    ]

    # Keywords indicating actual incidents (override regulatory detection)
    INCIDENT_KEYWORDS = {
        'sighted', 'observed', 'spotted', 'detected', 'seen',
        'intrusion', 'incursion', 'breach', 'violation',
        'closed', 'closure', 'shut down', 'grounded',
        'disruption', 'disrupted', 'interrupted',
        'evacuated', 'evacuation', 'emergency',

        # Danish
        'set', 'observeret', 'opdaget', 'spottet',
        'lukket', 'lukning', 'forstyrrelse',

        # Norwegian
        'sett', 'observert', 'oppdaget',
        'stengt', 'stenging', 'forstyrrelse',

        # Swedish
        'sedd', 'observerad', 'upptäckt',
        'stängd', 'stängning', 'störning',

        # German
        'gesichtet', 'beobachtet', 'entdeckt',
        'geschlossen', 'sperrung', 'störung',

        # French
        'vu', 'observé', 'détecté',
        'fermé', 'fermeture', 'perturbation',
    }

    def is_non_incident(self, incident: Dict) -> Tuple[bool, float, List[str]]:
        """
        Check if this is regulatory/advisory news rather than an actual incident.

        Returns:
            (is_non_incident, confidence, reasons)
        """
        title = incident.get('title', '').lower()
        narrative = incident.get('narrative', '').lower()
        text = f"{title} {narrative}"

        reasons = []
        regulatory_score = 0
        incident_score = 0

        # Check for regulatory keywords
        regulatory_keyword_count = 0
        for keyword in self.REGULATORY_KEYWORDS:
            if keyword in text:
                regulatory_keyword_count += 1
                regulatory_score += 1
                if regulatory_keyword_count == 1:  # Only add first match
                    reasons.append(f"Regulatory keyword: '{keyword}'")

        # Check for regulatory phrases
        for pattern in self.REGULATORY_PHRASES:
            if re.search(pattern, text, re.IGNORECASE):
                regulatory_score += 2
                reasons.append(f"Regulatory phrase pattern matched")
                break

        # Check for simulation keywords
        simulation_count = 0
        for keyword in self.SIMULATION_KEYWORDS:
            if keyword in text:
                simulation_count += 1
                regulatory_score += 2  # Simulations get higher weight
                if simulation_count == 1:  # Only add first match
                    reasons.append(f"Simulation keyword: '{keyword}'")

        # Check for simulation phrases (strong indicator)
        for pattern in self.SIMULATION_PHRASES:
            if re.search(pattern, text, re.IGNORECASE):
                regulatory_score += 3  # Phrases get even higher weight
                reasons.append(f"Simulation phrase pattern matched")
                break

        # Check for actual incident keywords (override)
        for keyword in self.INCIDENT_KEYWORDS:
            if keyword in text:
                incident_score += 2

        # Calculate confidence
        net_score = regulatory_score - incident_score

        # Enhanced logic for policy announcements:
        # Multiple regulatory keywords (2+) indicate policy announcement
        if regulatory_keyword_count >= 2 and net_score >= 2:
            confidence = min(0.9, 0.6 + (net_score * 0.1))
            return (True, confidence, reasons)
        elif net_score >= 3:
            confidence = min(0.9, 0.5 + (net_score * 0.1))
            return (True, confidence, reasons)
        elif net_score >= 1:
            confidence = 0.3 + (net_score * 0.1)
            return (True, confidence, reasons)
        else:
            return (False, 0.0, [])

    def filter_incidents(self, incidents: List[Dict], confidence_threshold: float = 0.5) -> Tuple[List[Dict], List[Dict]]:
        """
        Filter incidents, separating actual incidents from regulatory news.

        Returns:
            (actual_incidents, filtered_out)
        """
        actual_incidents = []
        filtered_out = []

        for incident in incidents:
            is_non, confidence, reasons = self.is_non_incident(incident)

            if is_non and confidence >= confidence_threshold:
                filtered_out.append({
                    **incident,
                    '_filter_reason': 'non_incident',
                    '_filter_confidence': confidence,
                    '_filter_details': reasons
                })
            else:
                actual_incidents.append(incident)

        return actual_incidents, filtered_out


def main():
    """Test non-incident filter"""
    test_incidents = [
        {
            'title': 'Mange ministre kommer til byen - giver nyt droneforbud',
            'narrative': 'Mange ministre kommer til byen - giver nyt droneforbud Flyver man med drone, skal man være ekstra opmærksom i Horsens-området de kommende uger.',
        },
        {
            'title': 'Copenhagen Airport - Major Drone Disruption',
            'narrative': '2-3 large drones observed in controlled airspace forcing nearly 4-hour suspension of flights from 8:46 PM to 12:30 AM.',
        },
        {
            'title': 'New drone restrictions announced for Oslo',
            'narrative': 'Norway announces new temporary flight restrictions for drones around government buildings.',
        },
        {
            'title': 'Drone spotted over Heathrow Airport',
            'narrative': 'A drone was sighted near Heathrow Airport runway, causing brief disruption to arrivals.',
        },
    ]

    filter = NonIncidentFilter()

    print("=== Non-Incident Filter Test ===\n")

    for idx, incident in enumerate(test_incidents, 1):
        is_non, confidence, reasons = filter.is_non_incident(incident)

        print(f"{idx}. {incident['title'][:60]}")
        print(f"   Non-incident: {is_non}")
        print(f"   Confidence: {confidence:.2f}")
        if reasons:
            print(f"   Reasons: {', '.join(reasons)}")
        print(f"   Result: {'❌ FILTER OUT' if is_non and confidence >= 0.5 else '✅ KEEP'}")
        print()


if __name__ == '__main__':
    main()
