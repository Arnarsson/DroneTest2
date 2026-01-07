'use client'

import { motion } from 'framer-motion'
import { ThemeToggle } from './ThemeToggle'
import { DroneWatchLogo } from './DroneWatchLogo'
import { AboutModal, useAboutModal } from './AboutModal'
import { logger } from '@/lib/logger'

interface HeaderProps {
  incidentCount: number
  isLoading: boolean
  currentView: 'map' | 'list' | 'analytics'
  onViewChange: (view: 'map' | 'list' | 'analytics') => void
}

export function Header({ incidentCount, isLoading, currentView, onViewChange }: HeaderProps) {
  logger.debug('[Header] Rendered with incidentCount:', incidentCount)
  logger.debug('[Header] isLoading:', isLoading)

  const { isOpen, openModal, closeModal } = useAboutModal()

  return (
    <div>
      <AboutModal isOpen={isOpen} onClose={closeModal} />
      <header className="sticky top-0 z-50 bg-gradient-to-b from-white/95 to-white/80 dark:from-gray-900/95 dark:to-gray-900/80 backdrop-blur-2xl border-b border-gray-200/70 dark:border-gray-800/70 shadow-soft transition-all">
      <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-14">
          {/* Logo and Title */}
          <motion.div
            className="flex items-center gap-4"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <h1 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2.5 tracking-tight">
              <DroneWatchLogo size="md" />
              <span className="hidden sm:inline">DroneWatch</span>
            </h1>
            <span className="hidden md:inline text-[10px] text-gray-500 dark:text-gray-400 font-semibold uppercase tracking-[0.1em] border-l border-gray-300 dark:border-gray-700 pl-4">
              Safety Through Transparency
            </span>
          </motion.div>

          {/* View Toggle - Center on Desktop */}
          <motion.div
            className="hidden md:flex items-center gap-0.5 bg-gray-100/80 dark:bg-gray-800/80 rounded-lg p-0.5"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.1 }}
          >
            <ViewTab
              active={currentView === 'map'}
              onClick={() => onViewChange('map')}
              label="MAP"
            />
            <ViewTab
              active={currentView === 'list'}
              onClick={() => onViewChange('list')}
              label="LIST"
            />
            <ViewTab
              active={currentView === 'analytics'}
              onClick={() => onViewChange('analytics')}
              label="ANALYTICS"
            />
          </motion.div>

          {/* Right Section */}
          <motion.div
            className="flex items-center gap-2 sm:gap-3"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: 0.2 }}
          >
            {/* Live indicator */}
            <div className="flex items-center gap-2 bg-gray-50 dark:bg-gray-800 px-2.5 py-1.5 rounded-md border border-gray-200 dark:border-gray-700">
              <div className={`h-1.5 w-1.5 rounded-full ${isLoading ? 'bg-amber-500 animate-pulse' : 'bg-emerald-500'} shadow-sm ${isLoading ? 'shadow-amber-500/50' : 'shadow-emerald-500/50'}`} />
              <span className="text-[11px] sm:text-xs font-bold text-gray-700 dark:text-gray-300 tracking-wide">
                {isLoading ? 'UPDATING' : incidentCount}
              </span>
            </div>

            {/* Theme toggle */}
            <ThemeToggle />

            {/* About button */}
            <button
              onClick={openModal}
              className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 p-1.5 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-all focus-ring"
              title="About DroneWatch"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>
          </motion.div>
        </div>

        {/* Mobile View Toggle */}
        <div className="md:hidden pb-2.5 flex items-center gap-0.5 bg-gray-100/80 dark:bg-gray-800/80 rounded-lg p-0.5">
          <ViewTab
            active={currentView === 'map'}
            onClick={() => onViewChange('map')}
            label="MAP"
            compact
          />
          <ViewTab
            active={currentView === 'list'}
            onClick={() => onViewChange('list')}
            label="LIST"
            compact
          />
          <ViewTab
            active={currentView === 'analytics'}
            onClick={() => onViewChange('analytics')}
            label="ANALYTICS"
            compact
          />
        </div>
      </div>
    </header>
    </div>
  )
}

interface ViewTabProps {
  active: boolean
  onClick: () => void
  label: string
  compact?: boolean
}

function ViewTab({ active, onClick, label, compact }: ViewTabProps) {
  return (
    <button
      onClick={onClick}
      aria-label={`Switch to ${label.toLowerCase()} view`}
      aria-current={active ? 'page' : undefined}
      className={`relative px-3 py-1.5 text-[10px] font-bold tracking-wider transition-all rounded-md focus-ring ${
        active
          ? 'text-white'
          : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
      } ${compact ? 'flex-1' : ''}`}
    >
      {active && (
        <motion.div
          layoutId="activeTab"
          className="absolute inset-0 bg-gradient-to-b from-blue-600 to-blue-700 rounded-md shadow-sm"
          transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
        />
      )}
      <span className="relative z-10">{label}</span>
    </button>
  )
}