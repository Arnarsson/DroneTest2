'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'
import { FilterState } from '@/types'
import { getEvidenceConfig, type EvidenceScore } from '@/constants/evidence'
import { logger } from '@/lib/logger'

interface FilterPanelProps {
  filters: FilterState
  onChange: (filters: FilterState) => void
  incidentCount: number
  isOpen: boolean
  onToggle: () => void
}

export function FilterPanel({ filters, onChange, incidentCount, isOpen, onToggle }: FilterPanelProps) {
  logger.debug('[FilterPanel] Rendered')
  logger.debug('[FilterPanel] incidentCount:', incidentCount)
  logger.debug('[FilterPanel] filters:', filters)
  logger.debug('[FilterPanel] isOpen:', isOpen)

  const [expandedSections, setExpandedSections] = useState({
    evidence: true,
    location: true,
    time: true,
  })


  const handleChange = (key: keyof FilterState, value: any) => {
    onChange({ ...filters, [key]: value })
  }

  const activeFilterCount = [
    filters.searchQuery.trim() !== '',
    filters.minEvidence > 1,
    filters.country !== 'all',
    filters.status !== 'all',
    filters.assetType !== null,
    filters.dateRange !== 'all'
  ].filter(Boolean).length

  const resetFilters = () => {
    onChange({
      searchQuery: '',
      minEvidence: 1,
      country: 'all',
      status: 'all',
      assetType: null,
      dateRange: 'all'
    })
  }

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }))
  }

  return (
    <>
      {/* Mobile: Floating Filter Button */}
      <motion.button
        onClick={onToggle}
        aria-label={`${isOpen ? 'Close' : 'Open'} filters${activeFilterCount > 0 ? ` (${activeFilterCount} active)` : ''}`}
        aria-expanded={isOpen}
        className="lg:hidden fixed bottom-20 right-4 z-[999] bg-gradient-to-br from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-full shadow-elevated p-4 transition-all"
        whileHover={{ scale: 1.08, rotate: 5 }}
        whileTap={{ scale: 0.95 }}
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ type: 'spring', bounce: 0.5 }}
      >
        <div className="flex items-center gap-2">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          {activeFilterCount > 0 && (
            <motion.span
              className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center"
              initial={{ scale: 0 }} 
              animate={{ scale: 1 }}
              transition={{ type: 'spring', bounce: 0.6 }}
            >
              {activeFilterCount}
            </motion.span>
          )}
        </div>
      </motion.button>

      {/* Filter Panel Overlay (Mobile) */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="lg:hidden fixed inset-0 bg-black/60 z-[998] backdrop-blur-sm"
            onClick={onToggle}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          />
        )}
      </AnimatePresence>

      {/* Filter Panel */}
      <motion.div
        className={`
          fixed lg:relative top-0 right-0 h-full
          bg-white/98 dark:bg-gray-900/98 backdrop-blur-2xl border-l border-gray-200/70 dark:border-gray-800/70
          shadow-elevated lg:shadow-soft
          z-[999] lg:z-auto
          w-80 lg:w-80
          overflow-y-auto
          ${isOpen ? 'translate-x-0' : 'translate-x-full lg:translate-x-0'}
          transition-transform duration-300 ease-out
        `}
        initial={false}
        transition={{ type: 'spring', damping: 30, stiffness: 300 }}
      >
        <div className="p-6 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Filters</h2>
              <motion.p
                className="text-sm text-gray-500 dark:text-gray-400 mt-1"
                key={incidentCount}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
              >
                {incidentCount} incident{incidentCount !== 1 ? 's' : ''} found
              </motion.p>
            </div>
            <button
              onClick={onToggle}
              className="lg:hidden p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Search Input */}
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              value={filters.searchQuery}
              onChange={(e) => handleChange('searchQuery', e.target.value)}
              placeholder="Search incidents..."
              aria-label="Search incidents by title, narrative, or location"
              className="w-full pl-10 pr-3 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            />
          </div>

          {/* Active Filters & Reset */}
          <AnimatePresence>
            {activeFilterCount > 0 && (
              <motion.div
                className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
              >
                <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
                  {activeFilterCount} active filter{activeFilterCount !== 1 ? 's' : ''}
                </span>
                <button
                  onClick={resetFilters}
                  className="text-sm text-blue-600 dark:text-blue-400 hover:underline font-semibold"
                >
                  Clear all
                </button>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Quick Filters */}
          <div>
            <label className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-3 block">
              Quick Filters
            </label>
            <div className="flex flex-wrap gap-2">
              <QuickFilterChip
                active={filters.assetType === 'airport'}
                onClick={() => handleChange('assetType', filters.assetType === 'airport' ? null : 'airport')}
                icon="✈️"
                label="Airports"
              />
              <QuickFilterChip
                active={filters.assetType === 'military'}
                onClick={() => handleChange('assetType', filters.assetType === 'military' ? null : 'military')}
                icon="🛡️"
                label="Military"
              />
              <QuickFilterChip
                active={filters.dateRange === 'day'}
                onClick={() => handleChange('dateRange', filters.dateRange === 'day' ? 'all' : 'day')}
                icon="🕐"
                label="Today"
              />
              <QuickFilterChip
                active={filters.minEvidence >= 3}
                onClick={() => handleChange('minEvidence', filters.minEvidence >= 3 ? 1 : 3)}
                icon="✓"
                label="Verified"
              />
            </div>
          </div>

          <hr className="border-gray-200 dark:border-gray-700" />

          {/* Evidence Level Section */}
          <FilterSection
            title="Evidence Level"
            isExpanded={expandedSections.evidence}
            onToggle={() => toggleSection('evidence')}
          >
            <div className="space-y-2">
              {[1, 2, 3, 4].map((level) => {
                const config = getEvidenceConfig(level as EvidenceScore)
                return (
                  <motion.button
                    key={level}
                    onClick={() => handleChange('minEvidence', level)}
                    className={`w-full text-left px-4 py-3 rounded-lg transition-all ${
                      filters.minEvidence === level
                        ? 'bg-blue-600 text-white shadow-md'
                        : 'bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">
                        {level === 1 ? '1 - All Levels' : `${level}+ ${config.shortLabel}`}
                      </span>
                      <div className={`w-3 h-3 rounded-full ${
                        filters.minEvidence === level ? 'bg-white' : config.bgClass
                      }`} />
                    </div>
                  </motion.button>
                )
              })}
            </div>
          </FilterSection>

          {/* Location Section */}
          <FilterSection
            title="Location"
            isExpanded={expandedSections.location}
            onToggle={() => toggleSection('location')}
          >
            <div className="space-y-3">
              <div>
                <label className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1.5 block">
                  Country
                </label>
                <select
                  value={filters.country}
                  onChange={(e) => handleChange('country', e.target.value)}
                  className="w-full px-3 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
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

              <div>
                <label className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1.5 block">
                  Location Type
                </label>
                <select
                  value={filters.assetType || ''}
                  onChange={(e) => handleChange('assetType', e.target.value || null)}
                  className="w-full px-3 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                >
                  <option value="">All Types</option>
                  <option value="airport">✈️ Airport</option>
                  <option value="harbor">⚓ Harbor</option>
                  <option value="military">🛡️ Military</option>
                  <option value="powerplant">⚡ Power Plant</option>
                  <option value="other">📍 Other</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1.5 block">
                  Status
                </label>
                <select
                  value={filters.status}
                  onChange={(e) => handleChange('status', e.target.value)}
                  className="w-full px-3 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                >
                  <option value="all">All Status</option>
                  <option value="active">Active</option>
                  <option value="resolved">Resolved</option>
                  <option value="unconfirmed">Unconfirmed</option>
                </select>
              </div>
            </div>
          </FilterSection>

          {/* Time Period Section */}
          <FilterSection
            title="Time Period"
            isExpanded={expandedSections.time}
            onToggle={() => toggleSection('time')}
          >
            <select
              value={filters.dateRange}
              defaultValue="all"
              onChange={(e) => handleChange('dateRange', e.target.value)}
              className="w-full px-3 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            >
              <option value="all">All Time</option>
              <option value="day">Last 24 Hours</option>
              <option value="week">Last 7 Days</option>
              <option value="month">Last 30 Days</option>
            </select>
          </FilterSection>
        </div>
      </motion.div>
    </>
  )
}

interface FilterSectionProps {
  title: string
  isExpanded: boolean
  onToggle: () => void
  children: React.ReactNode
}

function FilterSection({ title, isExpanded, onToggle, children }: FilterSectionProps) {
  return (
    <div>
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between mb-3 group"
      >
        <h3 className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
          {title}
        </h3>
        <motion.svg
          className="w-4 h-4 text-gray-500 dark:text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </motion.svg>
      </button>
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

interface QuickFilterChipProps {
  active: boolean
  onClick: () => void
  icon: string
  label: string
}

function QuickFilterChip({ active, onClick, icon, label }: QuickFilterChipProps) {
  return (
    <motion.button
      onClick={onClick}
      className={`px-3 py-2 text-sm rounded-full font-medium transition-all ${
        active
          ? 'bg-blue-600 text-white shadow-md'
          : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
      }`}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <span className="flex items-center gap-1.5">
        <span>{icon}</span>
        <span>{label}</span>
      </span>
    </motion.button>
  )
}
