'use client'

import { useMemo } from 'react'
import { format } from 'date-fns/format'
import { startOfDay } from 'date-fns/startOfDay'
import { eachDayOfInterval } from 'date-fns/eachDayOfInterval'
import { isWithinInterval } from 'date-fns/isWithinInterval'
import { differenceInDays } from 'date-fns/differenceInDays'
import type { Incident } from '@/types'
import { getEvidenceConfig, type EvidenceScore } from '@/constants/evidence'

interface AnalyticsProps {
  incidents: Incident[]
}

export function Analytics({ incidents }: AnalyticsProps) {
  const stats = useMemo(() => calculateStats(incidents), [incidents])

  return (
    <div className="bg-gray-50 dark:bg-gray-950 min-h-full p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Analytics Dashboard
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Real-time insights from {stats.total} verified drone incidents across Europe
          </p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard
            title="Total Incidents"
            value={stats.total}
            subtitle={`Across ${Object.keys(stats.byCountry).length} countries`}
            iconType="total"
            color="blue"
          />
          <StatCard
            title="Average Evidence"
            value={stats.avgEvidence.toFixed(1)}
            subtitle={`${stats.verified} verified (3-4)`}
            iconType="star"
            color="amber"
          />
          <StatCard
            title="Active Incidents"
            value={stats.byStatus.active || 0}
            subtitle={`${((stats.byStatus.active || 0) / stats.total * 100).toFixed(0)}% of total`}
            iconType="alert"
            color="red"
          />
          <StatCard
            title="Coverage Period"
            value={`${stats.daysCovered}d`}
            subtitle={stats.dateRange}
            iconType="calendar"
            color="indigo"
          />
        </div>

        {/* Charts Grid */}
        <div className="grid lg:grid-cols-2 gap-6 mb-6">
          {/* Incidents by Country */}
          <ChartCard title="Incidents by Country" subtitle="Distribution across European nations">
            <div className="space-y-3">
              {Object.entries(stats.byCountry)
                .sort(([, a], [, b]) => b - a)
                .map(([country, count]) => (
                  <BarItem
                    key={country}
                    label={country}
                    value={count}
                    percentage={((count / stats.total) * 100).toFixed(1)}
                    max={Math.max(...Object.values(stats.byCountry))}
                    color="blue"
                  />
                ))}
            </div>
          </ChartCard>

          {/* Incidents Over Time */}
          <ChartCard title="Incident Timeline" subtitle="Daily occurrence pattern">
            <TimelineChart incidents={incidents} />
          </ChartCard>

          {/* Evidence Distribution */}
          <ChartCard title="Evidence Quality Distribution" subtitle="Verification confidence levels">
            <div className="space-y-4">
              {Object.entries(stats.byEvidence)
                .sort(([a], [b]) => parseInt(b) - parseInt(a))
                .filter(([, count]) => count > 0)
                .map(([level, count]) => {
                  const percentage = ((count / stats.total) * 100).toFixed(1)
                  return (
                    <div key={level} className="space-y-2">
                      <BarItem
                        label={getEvidenceLabel(parseInt(level))}
                        value={count}
                        percentage={percentage}
                        max={Math.max(...Object.values(stats.byEvidence))}
                        color={getEvidenceColor(parseInt(level))}
                      />
                    </div>
                  )
                })}
            </div>
          </ChartCard>

          {/* Location Type Breakdown */}
          <ChartCard title="Critical Infrastructure Types" subtitle="Targeted locations">
            <div className="space-y-3">
              {Object.entries(stats.byAssetType)
                .sort(([, a], [, b]) => b - a)
                .filter(([, count]) => count > 0)
                .map(([type, count]) => (
                  <BarItem
                    key={type}
                    label={formatAssetType(type)}
                    value={count}
                    percentage={((count / stats.total) * 100).toFixed(1)}
                    max={Math.max(...Object.values(stats.byAssetType))}
                    color="emerald"
                  />
                ))}
            </div>
          </ChartCard>
        </div>

        {/* Key Insights */}
        <div className="grid lg:grid-cols-3 gap-6 mb-6">
          <InsightCard
            title="Most Affected Country"
            value={stats.topCountry.name}
            metric={`${stats.topCountry.count} incidents (${stats.topCountry.percentage}%)`}
            trend="high"
          />
          <InsightCard
            title="Primary Target Type"
            value={formatAssetType(stats.topAssetType.type)}
            metric={`${stats.topAssetType.count} incidents (${stats.topAssetType.percentage}%)`}
            trend="neutral"
          />
          <InsightCard
            title="Verification Rate"
            value={`${stats.verificationRate}%`}
            metric={`${stats.verified} of ${stats.total} incidents verified`}
            trend={stats.verificationRate >= 70 ? 'good' : 'neutral'}
          />
        </div>

        {/* Top Locations */}
        {stats.topLocations.length > 0 && (
          <ChartCard title="Hotspot Locations" subtitle="Areas with multiple incidents">
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {stats.topLocations.slice(0, 6).map((loc, idx) => (
                <div
                  key={idx}
                  className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-600 transition-all"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="font-semibold text-gray-900 dark:text-white text-sm mb-1 line-clamp-2">
                        {loc.name || 'Unknown Location'}
                      </div>
                      <div className="text-xs text-gray-600 dark:text-gray-400">
                        {loc.country}
                      </div>
                    </div>
                    <div className="ml-2 text-2xl font-bold text-blue-600 dark:text-blue-400">
                      {loc.count}
                    </div>
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-500">
                    {loc.lat.toFixed(4)}, {loc.lon.toFixed(4)}
                  </div>
                </div>
              ))}
            </div>
          </ChartCard>
        )}
      </div>
    </div>
  )
}

interface StatCardProps {
  title: string
  value: string | number
  subtitle: string
  iconType: 'total' | 'star' | 'alert' | 'calendar'
  color: 'blue' | 'amber' | 'red' | 'indigo'
}

function StatCard({ title, value, subtitle, iconType, color }: StatCardProps) {
  const colorClasses = {
    blue: 'bg-blue-500/10 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 border-blue-200 dark:border-blue-800',
    amber: 'bg-amber-500/10 dark:bg-amber-500/20 text-amber-600 dark:text-amber-400 border-amber-200 dark:border-amber-800',
    red: 'bg-red-500/10 dark:bg-red-500/20 text-red-600 dark:text-red-400 border-red-200 dark:border-red-800',
    indigo: 'bg-indigo-500/10 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 border-indigo-200 dark:border-indigo-800',
  }

  const icons = {
    total: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    star: (
      <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
      </svg>
    ),
    alert: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    ),
    calendar: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    ),
  }

  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl p-5 border border-gray-200 dark:border-gray-800 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className={`${colorClasses[color]} p-2.5 rounded-lg border`}>
          {icons[iconType]}
        </div>
      </div>
      <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">{value}</div>
      <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{title}</div>
      <div className="text-xs text-gray-500 dark:text-gray-500">{subtitle}</div>
    </div>
  )
}

interface ChartCardProps {
  title: string
  subtitle: string
  children: React.ReactNode
}

function ChartCard({ title, subtitle, children }: ChartCardProps) {
  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl p-6 border border-gray-200 dark:border-gray-800">
      <div className="mb-5">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">{title}</h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">{subtitle}</p>
      </div>
      {children}
    </div>
  )
}

interface InsightCardProps {
  title: string
  value: string
  metric: string
  trend: 'high' | 'good' | 'neutral'
}

function InsightCard({ title, value, metric, trend }: InsightCardProps) {
  const trendColors = {
    high: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800',
    good: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800',
    neutral: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800',
  }

  const trendIcons = {
    high: '▲',
    good: '✓',
    neutral: '●',
  }

  return (
    <div className={`${trendColors[trend]} rounded-xl p-5 border`}>
      <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{title}</div>
      <div className="text-2xl font-bold text-gray-900 dark:text-white mb-1 flex items-center gap-2">
        <span className="text-lg opacity-50">{trendIcons[trend]}</span>
        {value}
      </div>
      <div className="text-xs text-gray-600 dark:text-gray-400">{metric}</div>
    </div>
  )
}

interface BarItemProps {
  label: string
  value: number
  percentage: string
  max: number
  color: 'blue' | 'emerald' | 'amber' | 'orange' | 'red' | 'gray'
}

function BarItem({ label, value, percentage, max, color }: BarItemProps) {
  const barPercentage = (value / max) * 100

  const colorClasses = {
    blue: 'bg-blue-500 dark:bg-blue-600',
    emerald: 'bg-emerald-500 dark:bg-emerald-600',
    amber: 'bg-amber-500 dark:bg-amber-600',
    orange: 'bg-orange-500 dark:bg-orange-600',
    red: 'bg-red-500 dark:bg-red-600',
    gray: 'bg-gray-500 dark:bg-gray-600',
  }

  return (
    <div className="group">
      <div className="flex justify-between items-baseline text-sm mb-2">
        <span className="text-gray-700 dark:text-gray-300 font-medium group-hover:text-gray-900 dark:group-hover:text-white transition-colors">
          {label}
        </span>
        <div className="flex items-baseline gap-2">
          <span className="text-gray-900 dark:text-white font-bold">{value}</span>
          <span className="text-xs text-gray-500 dark:text-gray-500">({percentage}%)</span>
        </div>
      </div>
      <div className="h-3 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
        <div
          className={`h-full ${colorClasses[color]} transition-all duration-700 ease-out rounded-full`}
          style={{ width: `${barPercentage}%` }}
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

    const days = eachDayOfInterval({ start: startOfDay(minDate), end: startOfDay(maxDate) })

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

  if (data.length === 0) {
    return <div className="h-48 flex items-center justify-center text-gray-400">No timeline data available</div>
  }

  return (
    <div className="space-y-4">
      <div className="h-40 flex items-end justify-between gap-1 px-2">
        {data.map((day, idx) => {
          const height = day.count === 0 ? 4 : (day.count / maxCount) * 100

          return (
            <div
              key={idx}
              className="flex-1 group relative"
              style={{ height: '100%' }}
            >
              <div
                className="absolute bottom-0 left-0 right-0 bg-blue-500 dark:bg-blue-600 rounded-t hover:bg-blue-600 dark:hover:bg-blue-500 transition-all cursor-pointer"
                style={{ height: `${height}%` }}
                title={`${format(day.date, 'MMM d, yyyy')}: ${day.count} incident${day.count !== 1 ? 's' : ''}`}
              />
            </div>
          )
        })}
      </div>
      <div className="flex justify-between text-xs text-gray-500 dark:text-gray-500 px-2">
        <span>{format(data[0].date, 'MMM d')}</span>
        <span>{format(data[Math.floor(data.length / 2)].date, 'MMM d')}</span>
        <span>{format(data[data.length - 1].date, 'MMM d')}</span>
      </div>
    </div>
  )
}

// Helper functions
function calculateStats(incidents: Incident[]) {
  if (incidents.length === 0) {
    return {
      total: 0,
      byCountry: {},
      byAssetType: {},
      byEvidence: { 1: 0, 2: 0, 3: 0, 4: 0 },
      byStatus: {},
      topLocations: [],
      avgEvidence: 0,
      verified: 0,
      verificationRate: 0,
      topCountry: { name: 'N/A', count: 0, percentage: '0' },
      topAssetType: { type: 'unknown', count: 0, percentage: '0' },
      daysCovered: 0,
      dateRange: 'No data',
    }
  }

  const byCountry: Record<string, number> = {}
  const byAssetType: Record<string, number> = {}
  const byEvidence: Record<number, number> = { 1: 0, 2: 0, 3: 0, 4: 0 }
  const byStatus: Record<string, number> = {}
  const locationCounts: Record<string, { lat: number; lon: number; name?: string; country: string; count: number }> = {}

  const dates = incidents.map(inc => new Date(inc.occurred_at))
  const minDate = new Date(Math.min(...dates.map(d => d.getTime())))
  const maxDate = new Date(Math.max(...dates.map(d => d.getTime())))
  const daysCovered = differenceInDays(maxDate, minDate) + 1

  incidents.forEach((inc) => {
    byCountry[inc.country] = (byCountry[inc.country] || 0) + 1

    const assetType = inc.asset_type || 'unknown'
    byAssetType[assetType] = (byAssetType[assetType] || 0) + 1

    byEvidence[inc.evidence_score] = (byEvidence[inc.evidence_score] || 0) + 1

    byStatus[inc.status] = (byStatus[inc.status] || 0) + 1

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

  const avgEvidence = incidents.reduce((sum, inc) => sum + inc.evidence_score, 0) / incidents.length
  const verified = incidents.filter((inc) => inc.evidence_score >= 3).length
  const verificationRate = Math.round((verified / incidents.length) * 100)

  const topCountryEntry = Object.entries(byCountry).sort(([, a], [, b]) => b - a)[0] || ['N/A', 0]
  const topCountry = {
    name: topCountryEntry[0],
    count: topCountryEntry[1],
    percentage: ((topCountryEntry[1] / incidents.length) * 100).toFixed(1),
  }

  const topAssetEntry = Object.entries(byAssetType).sort(([, a], [, b]) => b - a)[0] || ['unknown', 0]
  const topAssetType = {
    type: topAssetEntry[0],
    count: topAssetEntry[1],
    percentage: ((topAssetEntry[1] / incidents.length) * 100).toFixed(1),
  }

  const dateRange = `${format(minDate, 'MMM d')} - ${format(maxDate, 'MMM d, yyyy')}`

  return {
    total: incidents.length,
    byCountry,
    byAssetType,
    byEvidence,
    byStatus,
    topLocations,
    avgEvidence,
    verified,
    verificationRate,
    topCountry,
    topAssetType,
    daysCovered,
    dateRange,
  }
}

function formatAssetType(type: string): string {
  const labels: Record<string, string> = {
    airport: 'Airport',
    harbor: 'Harbor/Port',
    military: 'Military Installation',
    powerplant: 'Power Plant',
    bridge: 'Bridge',
    prison: 'Prison',
    government: 'Government Building',
    infrastructure: 'Critical Infrastructure',
    residential: 'Residential Area',
    other: 'Other',
    unknown: 'Unknown',
  }
  return labels[type] || type.charAt(0).toUpperCase() + type.slice(1)
}

function getEvidenceLabel(level: number): string {
  const config = getEvidenceConfig(level as EvidenceScore)
  return `Level ${level} - ${config.shortLabel}`
}

function getEvidenceColor(level: number): 'gray' | 'amber' | 'orange' | 'red' | 'emerald' {
  // Map evidence levels to bar colors using EVIDENCE_SYSTEM
  // Level 4 (Official) = emerald, Level 3 (Verified) = amber
  // Level 2 (Reported) = orange, Level 1 (Unconfirmed) = red
  const colorMap: Record<number, 'gray' | 'amber' | 'orange' | 'red' | 'emerald'> = {
    4: 'emerald',  // Official - emerald (matches badge)
    3: 'amber',    // Verified - amber (matches badge)
    2: 'orange',   // Reported - orange (matches badge)
    1: 'red',      // Unconfirmed - red (matches badge)
  }
  return colorMap[level] || 'gray'
}