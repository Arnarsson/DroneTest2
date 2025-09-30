'use client'

import { useMemo } from 'react'
import { format, startOfDay, eachDayOfInterval, isWithinInterval } from 'date-fns'
import type { Incident } from '@/types'

interface AnalyticsProps {
  incidents: Incident[]
}

export function Analytics({ incidents }: AnalyticsProps) {
  const stats = useMemo(() => calculateStats(incidents), [incidents])

  return (
    <div className="bg-white border-t border-gray-200 p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Analytics Dashboard</h2>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard
          title="Total Incidents"
          value={stats.total}
          icon="🚁"
          color="blue"
        />
        <StatCard
          title="Avg Evidence Score"
          value={stats.avgEvidence.toFixed(1)}
          icon="⭐"
          color="yellow"
        />
        <StatCard
          title="Active"
          value={stats.byStatus.active || 0}
          icon="🔴"
          color="red"
        />
        <StatCard
          title="Verified (3-4)"
          value={stats.verified}
          icon="✓"
          color="green"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* By Country */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">By Country</h3>
          <div className="space-y-2">
            {Object.entries(stats.byCountry)
              .sort(([, a], [, b]) => b - a)
              .map(([country, count]) => (
                <BarItem
                  key={country}
                  label={country}
                  value={count}
                  max={Math.max(...Object.values(stats.byCountry))}
                  color="blue"
                />
              ))}
          </div>
        </div>

        {/* By Asset Type */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">By Location Type</h3>
          <div className="space-y-2">
            {Object.entries(stats.byAssetType)
              .sort(([, a], [, b]) => b - a)
              .map(([type, count]) => (
                <BarItem
                  key={type}
                  label={formatAssetType(type)}
                  value={count}
                  max={Math.max(...Object.values(stats.byAssetType))}
                  color="green"
                />
              ))}
          </div>
        </div>

        {/* Evidence Distribution */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Evidence Level</h3>
          <div className="space-y-2">
            {Object.entries(stats.byEvidence)
              .sort(([a], [b]) => parseInt(b) - parseInt(a))
              .map(([level, count]) => (
                <BarItem
                  key={level}
                  label={getEvidenceLabel(parseInt(level))}
                  value={count}
                  max={Math.max(...Object.values(stats.byEvidence))}
                  color={getEvidenceColor(parseInt(level))}
                />
              ))}
          </div>
        </div>

        {/* Timeline Chart */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Incidents Over Time</h3>
          <TimelineChart incidents={incidents} />
        </div>
      </div>

      {/* Top Locations */}
      {stats.topLocations.length > 0 && (
        <div className="mt-6 bg-gray-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Most Affected Locations</h3>
          <div className="grid md:grid-cols-3 gap-4">
            {stats.topLocations.slice(0, 6).map((loc, idx) => (
              <div key={idx} className="bg-white rounded p-3">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="font-medium text-gray-900">
                      {loc.name || `${loc.lat.toFixed(2)}, ${loc.lon.toFixed(2)}`}
                    </div>
                    <div className="text-sm text-gray-500">{loc.country}</div>
                  </div>
                  <div className="text-xl font-bold text-blue-600">{loc.count}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

interface StatCardProps {
  title: string
  value: string | number
  icon: string
  color: 'blue' | 'yellow' | 'red' | 'green'
}

function StatCard({ title, value, icon, color }: StatCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    yellow: 'bg-yellow-50 text-yellow-600',
    red: 'bg-red-50 text-red-600',
    green: 'bg-green-50 text-green-600',
  }

  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <div className="flex items-center gap-3">
        <div className={`text-3xl ${colorClasses[color]} w-12 h-12 rounded-lg flex items-center justify-center`}>
          {icon}
        </div>
        <div>
          <div className="text-2xl font-bold text-gray-900">{value}</div>
          <div className="text-sm text-gray-500">{title}</div>
        </div>
      </div>
    </div>
  )
}

interface BarItemProps {
  label: string
  value: number
  max: number
  color: 'blue' | 'green' | 'yellow' | 'orange' | 'red' | 'gray'
}

function BarItem({ label, value, max, color }: BarItemProps) {
  const percentage = (value / max) * 100

  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    orange: 'bg-orange-500',
    red: 'bg-red-500',
    gray: 'bg-gray-500',
  }

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-700 font-medium">{label}</span>
        <span className="text-gray-600">{value}</span>
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${colorClasses[color]} transition-all`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

function TimelineChart({ incidents }: { incidents: Incident[] }) {
  const data = useMemo(() => {
    if (incidents.length === 0) return []

    const dates = incidents.map((i) => new Date(i.occurred_at))
    const minDate = new Date(Math.min(...dates.map((d) => d.getTime())))
    const maxDate = new Date(Math.max(...dates.map((d) => d.getTime())))

    // Get all days in range
    const days = eachDayOfInterval({ start: startOfDay(minDate), end: startOfDay(maxDate) })

    // Count incidents per day
    return days.map((day) => {
      const dayStart = startOfDay(day)
      const dayEnd = new Date(dayStart)
      dayEnd.setHours(23, 59, 59, 999)

      const count = incidents.filter((inc) =>
        isWithinInterval(new Date(inc.occurred_at), { start: dayStart, end: dayEnd })
      ).length

      return { date: day, count }
    })
  }, [incidents])

  const maxCount = Math.max(...data.map((d) => d.count), 1)

  return (
    <div className="h-32 flex items-end justify-between gap-0.5">
      {data.map((day, idx) => {
        const height = day.count === 0 ? 2 : (day.count / maxCount) * 100

        return (
          <div
            key={idx}
            className="flex-1 bg-blue-500 rounded-t transition-all hover:bg-blue-600"
            style={{ height: `${height}%`, minHeight: '2px' }}
            title={`${format(day.date, 'MMM d')}: ${day.count} incident${day.count !== 1 ? 's' : ''}`}
          />
        )
      })}
    </div>
  )
}

// Helper functions
function calculateStats(incidents: Incident[]) {
  const byCountry: Record<string, number> = {}
  const byAssetType: Record<string, number> = {}
  const byEvidence: Record<number, number> = { 1: 0, 2: 0, 3: 0, 4: 0 }
  const byStatus: Record<string, number> = {}
  const locationCounts: Record<string, { lat: number; lon: number; name?: string; country: string; count: number }> = {}

  incidents.forEach((inc) => {
    // Country
    byCountry[inc.country] = (byCountry[inc.country] || 0) + 1

    // Asset type
    const assetType = inc.asset_type || 'unknown'
    byAssetType[assetType] = (byAssetType[assetType] || 0) + 1

    // Evidence
    byEvidence[inc.evidence_score] = (byEvidence[inc.evidence_score] || 0) + 1

    // Status
    byStatus[inc.status] = (byStatus[inc.status] || 0) + 1

    // Locations (group by name or coordinates)
    const locKey = inc.location_name || `${inc.lat.toFixed(3)},${inc.lon.toFixed(3)}`
    if (!locationCounts[locKey]) {
      locationCounts[locKey] = {
        lat: inc.lat,
        lon: inc.lon,
        name: inc.location_name,
        country: inc.country,
        count: 0,
      }
    }
    locationCounts[locKey].count++
  })

  const topLocations = Object.values(locationCounts)
    .sort((a, b) => b.count - a.count)
    .filter((loc) => loc.count > 1)

  const avgEvidence = incidents.length > 0
    ? incidents.reduce((sum, inc) => sum + inc.evidence_score, 0) / incidents.length
    : 0

  const verified = incidents.filter((inc) => inc.evidence_score >= 3).length

  return {
    total: incidents.length,
    byCountry,
    byAssetType,
    byEvidence,
    byStatus,
    topLocations,
    avgEvidence,
    verified,
  }
}

function formatAssetType(type: string): string {
  const icons: Record<string, string> = {
    airport: '✈️ Airport',
    harbor: '⚓ Harbor',
    military: '🛡️ Military',
    powerplant: '⚡ Power Plant',
    bridge: '🌉 Bridge',
    other: '📍 Other',
    unknown: '❓ Unknown',
  }
  return icons[type] || type
}

function getEvidenceLabel(level: number): string {
  const labels: Record<number, string> = {
    1: '1 - Unverified',
    2: '2 - OSINT',
    3: '3 - Verified',
    4: '4 - Official',
  }
  return labels[level] || `Level ${level}`
}

function getEvidenceColor(level: number): 'gray' | 'yellow' | 'orange' | 'red' {
  const colors: Record<number, 'gray' | 'yellow' | 'orange' | 'red'> = {
    1: 'gray',
    2: 'yellow',
    3: 'orange',
    4: 'red',
  }
  return colors[level] || 'gray'
}