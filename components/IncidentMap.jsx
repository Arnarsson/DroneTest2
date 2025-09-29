// Example React component showing how to use the API with Leaflet
import React, { useEffect, useState } from 'react';
import L from 'leaflet';
import { fetchIncidents, formatEvidenceLevel, formatIncidentDate } from '../lib/api';

export default function IncidentMap() {
  const [map, setMap] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize map
  useEffect(() => {
    if (!map && typeof window !== 'undefined') {
      const mapInstance = L.map('incident-map').setView([56.0, 10.5], 6); // Denmark center

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(mapInstance);

      setMap(mapInstance);
    }

    return () => {
      if (map) {
        map.remove();
      }
    };
  }, []);

  // Fetch and display incidents
  useEffect(() => {
    if (!map) return;

    const loadIncidents = async () => {
      try {
        setLoading(true);
        const data = await fetchIncidents({
          minEvidence: 2,
          country: 'DK',
          limit: 200
        });

        setIncidents(data);

        // Clear existing markers
        map.eachLayer((layer) => {
          if (layer instanceof L.Marker) {
            map.removeLayer(layer);
          }
        });

        // Add markers for each incident
        data.forEach(incident => {
          if (incident.lat && incident.lon) {
            const icon = L.divIcon({
              className: 'incident-marker',
              html: `<div class="evidence-${incident.evidence_score}">📍</div>`,
              iconSize: [30, 30]
            });

            const marker = L.marker([incident.lat, incident.lon], { icon })
              .addTo(map);

            // Create popup content
            const popupContent = `
              <div class="incident-popup">
                <h3>${incident.title}</h3>
                <p class="incident-time">${formatIncidentDate(incident.occurred_at)}</p>
                <p class="incident-evidence">
                  Evidence: ${formatEvidenceLevel(incident.evidence_score)} (${incident.evidence_score}/4)
                </p>
                ${incident.narrative ? `<p>${incident.narrative}</p>` : ''}
                ${incident.sources && incident.sources.length > 0 ? `
                  <div class="incident-sources">
                    <strong>Sources:</strong>
                    ${incident.sources.map(s => `
                      <a href="${s.source_url}" target="_blank" rel="noopener">
                        ${s.source_type} →
                      </a>
                    `).join(' ')}
                  </div>
                ` : ''}
              </div>
            `;

            marker.bindPopup(popupContent, {
              maxWidth: 300,
              className: 'incident-popup-container'
            });
          }
        });

        setLoading(false);
      } catch (err) {
        console.error('Failed to load incidents:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    loadIncidents();
  }, [map]);

  return (
    <div className="map-container">
      {loading && (
        <div className="map-loading">Loading incidents...</div>
      )}
      {error && (
        <div className="map-error">Error: {error}</div>
      )}
      <div id="incident-map" style={{ height: '600px', width: '100%' }} />

      <style jsx>{`
        .incident-popup h3 {
          margin: 0 0 8px 0;
          font-size: 16px;
        }
        .incident-time {
          color: #666;
          font-size: 12px;
        }
        .incident-evidence {
          font-weight: bold;
          margin: 8px 0;
        }
        .incident-sources a {
          margin-right: 8px;
          text-decoration: none;
          color: #0066cc;
        }
        .evidence-4 { color: #d32f2f; } /* Official - red */
        .evidence-3 { color: #f57c00; } /* Verified - orange */
        .evidence-2 { color: #fbc02d; } /* OSINT - yellow */
        .evidence-1 { color: #9e9e9e; } /* Unverified - gray */
      `}</style>
    </div>
  );
}