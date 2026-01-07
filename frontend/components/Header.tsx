'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ThemeToggle } from './ThemeToggle'
import { DroneWatchLogo } from './DroneWatchLogo'
import { AboutModal, useAboutModal } from './AboutModal'
import { logger } from '@/lib/logger'
import { SHORTCUT_KEYS } from '@/hooks/useKeyboardShortcuts'

/**
 * Keyboard shortcuts data for the help popover
 */
const KEYBOARD_SHORTCUTS = [
  { key: SHORTCUT_KEYS.MAP_VIEW, description: 'Map View' },
  { key: SHORTCUT_KEYS.LIST_VIEW, description: 'List View' },
  { key: SHORTCUT_KEYS.ANALYTICS_VIEW, description: 'Analytics View' },
  { key: SHORTCUT_KEYS.FILTER_TOGGLE, description: 'Toggle Filters', displayKey: 'F' },
]

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
              shortcutKey={SHORTCUT_KEYS.MAP_VIEW}
            />
            <ViewTab
              active={currentView === 'list'}
              onClick={() => onViewChange('list')}
              label="LIST"
              shortcutKey={SHORTCUT_KEYS.LIST_VIEW}
            />
            <ViewTab
              active={currentView === 'analytics'}
              onClick={() => onViewChange('analytics')}
              label="ANALYTICS"
              shortcutKey={SHORTCUT_KEYS.ANALYTICS_VIEW}
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

            {/* Keyboard shortcuts help */}
            <KeyboardShortcutsHelp />

            {/* About button */}
            <button
              onClick={openModal}
              className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 p-1.5 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-all"
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
            shortcutKey={SHORTCUT_KEYS.MAP_VIEW}
            compact
          />
          <ViewTab
            active={currentView === 'list'}
            onClick={() => onViewChange('list')}
            label="LIST"
            shortcutKey={SHORTCUT_KEYS.LIST_VIEW}
            compact
          />
          <ViewTab
            active={currentView === 'analytics'}
            onClick={() => onViewChange('analytics')}
            label="ANALYTICS"
            shortcutKey={SHORTCUT_KEYS.ANALYTICS_VIEW}
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
  shortcutKey: string
  compact?: boolean
}

function ViewTab({ active, onClick, label, shortcutKey, compact }: ViewTabProps) {
  return (
    <button
      onClick={onClick}
      aria-label={`Switch to ${label.toLowerCase()} view (press ${shortcutKey})`}
      aria-keyshortcuts={shortcutKey}
      aria-current={active ? 'page' : undefined}
      className={`relative px-3 py-1.5 text-[10px] font-bold tracking-wider transition-all ${
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
      <span className="relative z-10 flex items-center gap-1.5">
        {label}
        <kbd
          className={`inline-flex items-center justify-center min-w-[16px] h-4 px-1 text-[9px] font-medium rounded border ${
            active
              ? 'bg-white/20 border-white/30 text-white/90'
              : 'bg-gray-200/60 dark:bg-gray-700/60 border-gray-300/70 dark:border-gray-600/70 text-gray-500 dark:text-gray-400'
          }`}
        >
          {shortcutKey}
        </kbd>
      </span>
    </button>
  )
}

/**
 * Keyboard shortcuts help indicator with popover
 * Shows available keyboard shortcuts on hover or click
 */
function KeyboardShortcutsHelp() {
  const [isOpen, setIsOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)

  // Close on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false)
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isOpen])

  // Close on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false)
      }
    }
    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isOpen])

  // Clean up timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  const handleMouseEnter = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
    timeoutRef.current = setTimeout(() => {
      setIsOpen(true)
    }, 200)
  }

  const handleMouseLeave = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
    timeoutRef.current = setTimeout(() => {
      setIsOpen(false)
    }, 150)
  }

  const handleClick = () => {
    setIsOpen(!isOpen)
  }

  return (
    <div
      ref={containerRef}
      className="relative"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <button
        onClick={handleClick}
        className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 p-1.5 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-all"
        title="Keyboard Shortcuts"
        aria-label="Show keyboard shortcuts"
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.95 }}
            transition={{ duration: 0.15, ease: 'easeOut' }}
            className="absolute right-0 top-full mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-2 z-50"
            role="tooltip"
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
          >
            <div className="px-3 py-1.5 border-b border-gray-200 dark:border-gray-700">
              <span className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                Keyboard Shortcuts
              </span>
            </div>
            <ul className="py-1">
              {KEYBOARD_SHORTCUTS.map((shortcut) => (
                <li
                  key={shortcut.key}
                  className="flex items-center justify-between px-3 py-1.5 text-sm"
                >
                  <span className="text-gray-600 dark:text-gray-400">
                    {shortcut.description}
                  </span>
                  <kbd className="inline-flex items-center justify-center min-w-[20px] h-5 px-1.5 text-[10px] font-semibold bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded text-gray-700 dark:text-gray-300">
                    {shortcut.displayKey || shortcut.key}
                  </kbd>
                </li>
              ))}
            </ul>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}