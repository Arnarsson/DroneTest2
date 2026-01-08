import { FilterState } from '@/types'

interface FiltersProps {
  filters: FilterState
  onChange: (filters: FilterState) => void
  view: 'map' | 'list' | 'analytics'
  onViewChange: (view: 'map' | 'list' | 'analytics') => void
}

export function Filters({ filters, onChange, view, onViewChange }: FiltersProps) {
  const handleChange = (key: keyof FilterState, value: any) => {
    onChange({ ...filters, [key]: value })
  }

  const selectClass = "text-sm border border-gray-300 dark:border-gray-700 rounded-md px-3 py-1.5 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600 transition-colors"
  const labelClass = "text-xs text-gray-500 dark:text-gray-400 mb-1"

  return (
    <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
        <div className="flex flex-wrap items-center gap-3">
          {/* Evidence Level */}
          <div className="flex flex-col">
            <label className={labelClass}>Evidence</label>
            <select
              value={filters.minEvidence}
              onChange={(e) => handleChange('minEvidence', parseInt(e.target.value))}
              className={selectClass}
            >
              <option value="1">All Levels</option>
              <option value="2">OSINT+ (≥2)</option>
              <option value="3">Verified (≥3)</option>
              <option value="4">Official Only (4)</option>
            </select>
          </div>

          {/* Country */}
          <div className="flex flex-col">
            <label className={labelClass}>Country</label>
            <select
              value={filters.country}
              onChange={(e) => handleChange('country', e.target.value)}
              className={selectClass}
            >
              <option value="all">All Countries</option>
              <option value="DK">Denmark 🇩🇰</option>
              <option value="NO">Norway 🇳🇴</option>
              <option value="SE">Sweden 🇸🇪</option>
              <option value="FI">Finland 🇫🇮</option>
              <option value="PL">Poland 🇵🇱</option>
              <option value="NL">Netherlands 🇳🇱</option>
            </select>
          </div>

          {/* Status */}
          <div className="flex flex-col">
            <label className={labelClass}>Status</label>
            <select
              value={filters.status}
              onChange={(e) => handleChange('status', e.target.value)}
              className={selectClass}
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="resolved">Resolved</option>
              <option value="unconfirmed">Unconfirmed</option>
            </select>
          </div>

          {/* Asset Type */}
          <div className="flex flex-col">
            <label className={labelClass}>Location</label>
            <select
              value={filters.assetType || ''}
              onChange={(e) => handleChange('assetType', e.target.value || null)}
              className={selectClass}
            >
              <option value="">All Types</option>
              <option value="airport">✈️ Airport</option>
              <option value="harbor">⚓ Harbor</option>
              <option value="military">🛡️ Military</option>
              <option value="powerplant">⚡ Power Plant</option>
              <option value="other">📍 Other</option>
            </select>
          </div>

          {/* Time Range */}
          <div className="flex flex-col">
            <label className={labelClass}>Time</label>
            <select
              value={filters.dateRange}
              onChange={(e) => handleChange('dateRange', e.target.value)}
              className={selectClass}
            >
              <option value="day">Last 24h</option>
              <option value="week">Last Week</option>
              <option value="month">Last Month</option>
              <option value="all">All Time</option>
            </select>
          </div>

          {/* Spacer */}
          <div className="flex-1" />

          {/* View Toggle */}
          <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-0.5 transition-colors">
            <button
              onClick={() => onViewChange('map')}
              className={`focus-ring px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                view === 'map'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              🗺️ Map
            </button>
            <button
              onClick={() => onViewChange('list')}
              className={`focus-ring px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                view === 'list'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              📋 List
            </button>
            <button
              onClick={() => onViewChange('analytics')}
              className={`focus-ring px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                view === 'analytics'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              📊 Analytics
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}