'use client'

import { motion } from 'framer-motion'
import { ThemeToggle } from './ThemeToggle'

interface HeaderProps {
  incidentCount: number
  isLoading: boolean
  currentView: 'map' | 'list' | 'analytics'
  onViewChange: (view: 'map' | 'list' | 'analytics') => void
}

export function Header({ incidentCount, isLoading, currentView, onViewChange }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 bg-gradient-to-b from-white/95 to-white/80 dark:from-gray-900/95 dark:to-gray-900/80 backdrop-blur-2xl border-b border-gray-200/70 dark:border-gray-800/70 shadow-soft transition-all">
      <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Title */}
          <motion.div
            className="flex items-center gap-4"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <span className="text-3xl">🚁</span>
              <span className="hidden sm:inline">DroneWatch</span>
            </h1>
            <span className="hidden md:inline text-sm text-gray-500 dark:text-gray-400 font-medium">
              Real-time drone incident tracking
            </span>
          </motion.div>

          {/* View Toggle - Center on Desktop */}
          <motion.div
            className="hidden md:flex items-center gap-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.1 }}
          >
            <ViewTab
              active={currentView === 'map'}
              onClick={() => onViewChange('map')}
              icon="🗺️"
              label="Map"
            />
            <ViewTab
              active={currentView === 'list'}
              onClick={() => onViewChange('list')}
              icon="📋"
              label="List"
            />
            <ViewTab
              active={currentView === 'analytics'}
              onClick={() => onViewChange('analytics')}
              icon="📊"
              label="Analytics"
            />
          </motion.div>

          {/* Right Section */}
          <motion.div
            className="flex items-center gap-3 sm:gap-4"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: 0.2 }}
          >
            {/* Live indicator */}
            <div className="flex items-center gap-2 bg-gray-50 dark:bg-gray-800 px-3 py-1.5 rounded-lg">
              <div className={`h-2.5 w-2.5 rounded-full ${isLoading ? 'bg-yellow-400 animate-pulse' : 'bg-green-500'} shadow-lg ${isLoading ? 'shadow-yellow-400/50' : 'shadow-green-500/50'}`} />
              <span className="text-xs sm:text-sm font-semibold text-gray-700 dark:text-gray-300">
                {isLoading ? 'Updating' : `${incidentCount}`}
              </span>
            </div>

            {/* Theme toggle */}
            <ThemeToggle />

            {/* Info button */}
            <button
              onClick={() => window.open('/about', '_blank')}
              className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-all"
              title="About DroneWatch"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>
          </motion.div>
        </div>

        {/* Mobile View Toggle */}
        <div className="md:hidden pb-3 flex items-center gap-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
          <ViewTab
            active={currentView === 'map'}
            onClick={() => onViewChange('map')}
            icon="🗺️"
            label="Map"
            compact
          />
          <ViewTab
            active={currentView === 'list'}
            onClick={() => onViewChange('list')}
            icon="📋"
            label="List"
            compact
          />
          <ViewTab
            active={currentView === 'analytics'}
            onClick={() => onViewChange('analytics')}
            icon="📊"
            label="Analytics"
            compact
          />
        </div>
      </div>
    </header>
  )
}

interface ViewTabProps {
  active: boolean
  onClick: () => void
  icon: string
  label: string
  compact?: boolean
}

function ViewTab({ active, onClick, icon, label, compact }: ViewTabProps) {
  return (
    <button
      onClick={onClick}
      className={`relative px-4 py-2 text-sm font-medium rounded-md transition-all ${
        active
          ? 'text-white shadow-md'
          : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
      } ${compact ? 'flex-1' : ''}`}
    >
      {active && (
        <motion.div
          layoutId="activeTab"
          className="absolute inset-0 bg-blue-600 rounded-md"
          transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
        />
      )}
      <span className="relative z-10 flex items-center justify-center gap-1.5">
        <span>{icon}</span>
        <span className={compact ? 'text-xs' : ''}>{label}</span>
      </span>
    </button>
  )
}