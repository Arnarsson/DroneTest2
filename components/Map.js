import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: '/leaflet/marker-icon-2x.png',
  iconUrl: '/leaflet/marker-icon.png',
  shadowUrl: '/leaflet/marker-shadow.png',
});

export default function Map({ incidents, loading }) {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersRef = useRef([]);

  // Initialize map
  useEffect(() => {
    if (!mapInstanceRef.current && mapRef.current) {
      mapInstanceRef.current = L.map(mapRef.current).setView([56.0, 10.5], 6);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(mapInstanceRef.current);
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Update markers when incidents change
  useEffect(() => {
    if (!mapInstanceRef.current) return;

    // Clear existing markers
    markersRef.current.forEach(marker => marker.remove());
    markersRef.current = [];

    // Add new markers
    incidents.forEach(incident => {
      if (incident.lat && incident.lon) {
        // Create custom icon based on evidence score
        const iconHtml = `
          <div class="incident-marker evidence-${incident.evidence_score}">
            <div style="
              width: 30px;
              height: 30px;
              border-radius: 50%;
              background: ${getEvidenceColor(incident.evidence_score)};
              border: 2px solid white;
              box-shadow: 0 2px 4px rgba(0,0,0,0.3);
              display: flex;
              align-items: center;
              justify-content: center;
              color: white;
              font-weight: bold;
            ">
              ${incident.evidence_score}
            </div>
          </div>
        `;

        const icon = L.divIcon({
          html: iconHtml,
          className: 'custom-marker',
          iconSize: [30, 30],
          iconAnchor: [15, 15]
        });

        const marker = L.marker([incident.lat, incident.lon], { icon })
          .addTo(mapInstanceRef.current);

        // Format date
        const date = new Date(incident.occurred_at);
        const formattedDate = date.toLocaleString('en-US', {
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });

        // Create popup
        const popupContent = `
          <div style="max-width: 300px;">
            <h3 style="margin: 0 0 8px 0; font-size: 16px; font-weight: bold;">
              ${incident.title}
            </h3>
            <p style="margin: 4px 0; color: #666; font-size: 12px;">
              ${formattedDate}
            </p>
            <p style="margin: 8px 0; font-size: 14px;">
              ${incident.narrative || 'No details available'}
            </p>
            <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #eee;">
              <span style="
                display: inline-block;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
                color: white;
                background: ${getEvidenceColor(incident.evidence_score)};
              ">
                Evidence: ${getEvidenceLabel(incident.evidence_score)}
              </span>
              ${incident.asset_type ? `
                <span style="
                  display: inline-block;
                  margin-left: 8px;
                  padding: 2px 8px;
                  border-radius: 12px;
                  font-size: 12px;
                  background: #f3f4f6;
                  color: #4b5563;
                ">
                  ${incident.asset_type}
                </span>
              ` : ''}
            </div>
          </div>
        `;

        marker.bindPopup(popupContent, {
          maxWidth: 300,
          className: 'incident-popup'
        });

        markersRef.current.push(marker);
      }
    });

    // Fit bounds if we have markers
    if (markersRef.current.length > 0) {
      const group = L.featureGroup(markersRef.current);
      mapInstanceRef.current.fitBounds(group.getBounds().pad(0.1));
    }
  }, [incidents]);

  // Helper functions
  function getEvidenceColor(score) {
    switch(score) {
      case 4: return '#dc2626'; // red - official
      case 3: return '#ea580c'; // orange - verified
      case 2: return '#facc15'; // yellow - OSINT
      default: return '#9ca3af'; // gray - unverified
    }
  }

  function getEvidenceLabel(score) {
    switch(score) {
      case 4: return 'Official';
      case 3: return 'Verified Media';
      case 2: return 'OSINT';
      default: return 'Unverified';
    }
  }

  return (
    <div style={{ position: 'relative', height: 'calc(100vh - 200px)' }}>
      {loading && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          zIndex: 1000,
          background: 'white',
          padding: '20px',
          borderRadius: '8px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
        }}>
          <div>Loading incidents...</div>
        </div>
      )}
      <div ref={mapRef} style={{ height: '100%', width: '100%' }} />
    </div>
  );
}