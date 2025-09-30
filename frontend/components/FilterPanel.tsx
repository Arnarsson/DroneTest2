'use client'

import { useState } from 'react'
import { FilterState } from '@/types'

interface FilterPanelProps {
  filters: FilterState
  onChange: (filters: FilterState) => void
  incidentCount: number
  isOpen: boolean
  onToggle: () => void
}

export function FilterPanel({ filters, onChange, incidentCount, isOpen, onToggle }: FilterPanelProps) {
  const handleChange = (key: keyof FilterState, value: any) => {
    onChange({ ...filters, [key]: value })
  }

  const activeFilterCount = [
    filters.minEvidence > 1,
    filters.country !== 'all',
    filters.status !== 'all',
    filters.assetType !== null,
    filters.dateRange !== 'all'
  ].filter(Boolean).length

  const resetFilters = () => {
    onChange({
      minEvidence: 1,
      country: 'all',
      status: 'all',
      assetType: null,
      dateRange: 'all'
    })
  }

  return (
    <>
      {/* Mobile: Floating Filter Button */}
      <button
        onClick={onToggle}
        className="lg:hidden fixed bottom-6 right-6 z-[999] bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-2xl p-4 transition-all"
      >
        <div className="flex items-center gap-2">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          {activeFilterCount > 0 && (
            <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center">
              {activeFilterCount}
            </span>
          )}
        </div>
      </button>

      {/* Filter Panel Overlay (Mobile) */}
      {isOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/50 z-[998] backdrop-blur-sm"
          onClick={onToggle}
        />
      )}

      {/* Filter Panel */}
      <div className={`
        fixed lg:relative top-0 right-0 h-full
        bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-800
        shadow-2xl lg:shadow-none
        transition-transform duration-300 ease-in-out
        z-[999] lg:z-auto
        w-80 lg:w-72
        overflow-y-auto
        ${isOpen ? 'translate-x-0' : 'translate-x-full lg:translate-x-0'}
      `}>
        <div className="p-4 space-y-4">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-gray-900 dark:text-white">Filters</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {incidentCount} incident{incidentCount !== 1 ? 's' : ''}
              </p>
            </div>
            <button
              onClick={onToggle}
              className="lg:hidden p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Active Filters & Reset */}
          {activeFilterCount > 0 && (
            <div className="flex items-center justify-between p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <span className="text-sm text-blue-700 dark:text-blue-300">
                {activeFilterCount} filter{activeFilterCount !== 1 ? 's' : ''} active
              </span>
              <button
                onClick={resetFilters}
                className="text-sm text-blue-600 dark:text-blue-400 hover:underline font-medium"
              >
                Clear all
              </button>
            </div>
          )}

          {/* Quick Filters */}
          <div>
            <label className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-2 block">
              Quick Filters
            </label>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => handleChange('assetType', 'airport')}
                className={`px-3 py-1.5 text-sm rounded-full transition-colors ${
                  filters.assetType === 'airport'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                ✈️ Airports
              </button>
              <button
                onClick={() => handleChange('assetType', 'military')}
                className={`px-3 py-1.5 text-sm rounded-full transition-colors ${
                  filters.assetType === 'military'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                🛡️ Military
              </button>
              <button
                onClick={() => handleChange('dateRange', 'day')}
                className={`px-3 py-1.5 text-sm rounded-full transition-colors ${
                  filters.dateRange === 'day'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                🕐 Today
              </button>
              <button
                onClick={() => handleChange('minEvidence', 3)}
                className={`px-3 py-1.5 text-sm rounded-full transition-colors ${
                  filters.minEvidence >= 3
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                ✓ Verified Only
              </button>
            </div>
          </div>

          <hr className="border-gray-200 dark:border-gray-700" />

          {/* Evidence Level */}
          <div>
            <label className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-2 block">
              Evidence Level
            </label>
            <div className="space-y-2">
              {[1, 2, 3, 4].map((level) => (
                <button
                  key={level}
                  onClick={() => handleChange('minEvidence', level)}
                  className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                    filters.minEvidence === level
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">
                      {level === 1 && '1 - All Levels'}
                      {level === 2 && '2+ OSINT'}
                      {level === 3 && '3+ Verified'}
                      {level === 4 && '4 Official Only'}
                    </span>
                    <div className={`w-3 h-3 rounded-full ${
                      level === 1 && 'bg-gray-400'
                    }${level === 2 && 'bg-yellow-400'}${
                      level === 3 && 'bg-orange-500'
                    }${level === 4 && 'bg-red-600'}`} />
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Country */}
          <div>
            <label className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-2 block">
              Country
            </label>
            <select
              value={filters.country}
              onChange={(e) => handleChange('country', e.target.value)}
              className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Countries</option>
              <option value="DK">🇩🇰 Denmark</option>
              <option value="NO">🇳🇴 Norway</option>
              <option value="SE">🇸🇪 Sweden</option>
              <option value="FI">🇫🇮 Finland</option>
              <option value="PL">🇵🇱 Poland</option>
              <option value="NL">🇳🇱 Netherlands</option>
            </select>
          </div>

          {/* Status */}
          <div>
            <label className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-2 block">
              Status
            </label>
            <select
              value={filters.status}
              onChange={(e) => handleChange('status', e.target.value)}
              className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="resolved">Resolved</option>
              <option value="unconfirmed">Unconfirmed</option>
            </select>
          </div>

          {/* Location Type */}
          <div>
            <label className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-2 block">
              Location Type
            </label>
            <select
              value={filters.assetType || ''}
              onChange={(e) => handleChange('assetType', e.target.value || null)}
              className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500"
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
          <div>
            <label className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-2 block">
              Time Period
            </label>
            <select
              value={filters.dateRange}
              onChange={(e) => handleChange('dateRange', e.target.value)}
              className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500"
            >
              <option value="day">Last 24 Hours</option>
              <option value="week">Last 7 Days</option>
              <option value="month">Last 30 Days</option>
              <option value="all">All Time</option>
            </select>
          </div>
        </div>
      </div>
    </>
  )
}