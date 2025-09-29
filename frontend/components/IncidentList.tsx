import { format } from 'date-fns'
import type { Incident } from '@/types'

interface IncidentListProps {
  incidents: Incident[]
  isLoading: boolean
}

export function IncidentList({ incidents, isLoading }: IncidentListProps) {
  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-white rounded-lg shadow mb-4 p-6">
            <div className="skeleton h-6 w-3/4 mb-3 rounded" />
            <div className="skeleton h-4 w-1/2 mb-2 rounded" />
            <div className="skeleton h-4 w-full rounded" />
          </div>
        ))}
      </div>
    )
  }

  if (incidents.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <p className="text-gray-500 text-lg">No incidents found</p>
          <p className="text-gray-400 text-sm mt-2">Try adjusting your filters</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-6">
      <div className="space-y-4">
        {incidents.map((incident) => (
          <IncidentCard key={incident.id} incident={incident} />
        ))}
      </div>
    </div>
  )
}

function IncidentCard({ incident }: { incident: Incident }) {
  const evidenceLabels = {
    1: 'Unverified',
    2: 'OSINT',
    3: 'Verified Media',
    4: 'Official',
  }

  const evidenceColors = {
    1: 'bg-gray-500',
    2: 'bg-yellow-500',
    3: 'bg-orange-500',
    4: 'bg-red-600',
  }

  return (
    <div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-semibold text-gray-900">
          {incident.title}
        </h3>
        <div className="flex gap-2">
          <span className={`${evidenceColors[incident.evidence_score as keyof typeof evidenceColors]} text-white text-xs px-2 py-1 rounded-full font-medium`}>
            {evidenceLabels[incident.evidence_score as keyof typeof evidenceLabels]}
          </span>
          {incident.asset_type && (
            <span className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded-full">
              {incident.asset_type}
            </span>
          )}
        </div>
      </div>

      {incident.narrative && (
        <p className="text-gray-600 mb-3 line-clamp-2">
          {incident.narrative}
        </p>
      )}

      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-4 text-gray-500">
          <span>📍 {incident.location_name || `${incident.lat.toFixed(4)}, ${incident.lon.toFixed(4)}`}</span>
          <span>🕐 {format(new Date(incident.occurred_at), 'MMM d, HH:mm')}</span>
          <span>🌍 {incident.country}</span>
        </div>

        {incident.sources && incident.sources.length > 0 && (
          <div className="flex gap-2">
            {incident.sources.slice(0, 3).map((source, idx) => (
              <a
                key={idx}
                href={source.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 text-sm"
              >
                {source.source_type} →
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}