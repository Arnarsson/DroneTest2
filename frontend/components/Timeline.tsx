'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { format, startOfDay, endOfDay, isWithinInterval } from 'date-fns'
import type { Incident } from '@/types'

interface TimelineProps {
  incidents: Incident[]
  onTimeRangeChange: (start: Date | null, end: Date | null) => void
  isOpen: boolean
  onToggle: () => void
}

type PlaySpeed = 1 | 2 | 5 | 10

export function Timeline({ incidents, onTimeRangeChange, isOpen, onToggle }: TimelineProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [playSpeed, setPlaySpeed] = useState<PlaySpeed>(1)
  const [currentDate, setCurrentDate] = useState<Date | null>(null)
  const intervalRef = useRef<NodeJS.Timeout>()

  // Calculate date range from incidents
  const { minDate, maxDate, dateRange } = useIncidentDateRange(incidents)

  // Handle animation playback
  useEffect(() => {
    if (!isPlaying || !currentDate || !maxDate) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
      return
    }

    const intervalMs = 1000 / playSpeed
    intervalRef.current = setInterval(() => {
      setCurrentDate((prev) => {
        if (!prev || !maxDate) return prev

        const nextDate = new Date(prev)
        nextDate.setDate(nextDate.getDate() + 1)

        if (nextDate > maxDate) {
          setIsPlaying(false)
          return maxDate
        }

        return nextDate
      })
    }, intervalMs)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [isPlaying, playSpeed, maxDate])

  // Update filter when current date changes
  useEffect(() => {
    if (currentDate) {
      const start = startOfDay(currentDate)
      const end = endOfDay(currentDate)
      onTimeRangeChange(start, end)
    } else {
      onTimeRangeChange(null, null)
    }
  }, [currentDate, onTimeRangeChange])

  const handleReset = useCallback(() => {
    setIsPlaying(false)
    setCurrentDate(null)
  }, [])

  const handleShowAll = useCallback(() => {
    setIsPlaying(false)
    setCurrentDate(null)
  }, [])

  const handleDateChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setIsPlaying(false)
    const dayIndex = parseInt(e.target.value)
    if (dateRange[dayIndex]) {
      setCurrentDate(dateRange[dayIndex].date)
    }
  }, [dateRange])

  const togglePlay = useCallback(() => {
    if (!currentDate && minDate) {
      setCurrentDate(minDate)
    }
    setIsPlaying((prev) => !prev)
  }, [currentDate, minDate])

  const cycleSpeed = useCallback(() => {
    setPlaySpeed((prev) => {
      const speeds: PlaySpeed[] = [1, 2, 5, 10]
      const currentIndex = speeds.indexOf(prev)
      return speeds[(currentIndex + 1) % speeds.length]
    })
  }, [])

  if (!minDate || !maxDate || incidents.length === 0) {
    return null
  }

  const currentDayIndex = currentDate
    ? dateRange.findIndex((d) => d.date.getTime() === startOfDay(currentDate).getTime())
    : 0

  const incidentsOnCurrentDay = currentDate
    ? incidents.filter((inc) =>
        isWithinInterval(new Date(inc.occurred_at), {
          start: startOfDay(currentDate),
          end: endOfDay(currentDate),
        })
      )
    : []

  return (
    <motion.div
      className="fixed bottom-0 left-0 right-0 bg-white/98 dark:bg-gray-900/98 backdrop-blur-2xl border-t border-gray-200/70 dark:border-gray-800/70 shadow-elevated z-40"
      initial={{ y: 100 }}
      animate={{ y: 0 }}
      exit={{ y: 100 }}
      transition={{ type: 'spring', damping: 25, stiffness: 300 }}
    >
      {/* Toggle Button */}
      <button
        onClick={onToggle}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors group"
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl">⏱️</span>
          <div>
            <div className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              Timeline
              {currentDate && (
                <span className="text-sm font-normal text-gray-500 dark:text-gray-400">
                  {format(currentDate, 'MMM d, yyyy')}
                </span>
              )}
            </div>
            {currentDate && (
              <div className="text-xs text-gray-500 dark:text-gray-400">
                {incidentsOnCurrentDay.length} incident{incidentsOnCurrentDay.length !== 1 ? 's' : ''} on this day
              </div>
            )}
          </div>
        </div>
        <motion.svg
          className="w-5 h-5 text-gray-500 dark:text-gray-400 group-hover:text-gray-700 dark:group-hover:text-gray-300 transition-colors"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </motion.svg>
      </button>

      {/* Timeline Controls */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="px-4 pb-4 space-y-4"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
          >
            {/* Slider */}
            <div className="relative px-1">
              <input
                type="range"
                min={0}
                max={dateRange.length - 1}
                value={currentDayIndex}
                onChange={handleDateChange}
                className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer slider accent-blue-600"
                style={{
                  background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${(currentDayIndex / (dateRange.length - 1)) * 100}%, #e5e7eb ${(currentDayIndex / (dateRange.length - 1)) * 100}%, #e5e7eb 100%)`
                }}
              />

              {/* Date markers */}
              <div className="flex justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
                <span>{format(minDate, 'MMM d, yyyy')}</span>
                <span>{format(maxDate, 'MMM d, yyyy')}</span>
              </div>
            </div>

            {/* Controls Row */}
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                {/* Play/Pause */}
                <motion.button
                  onClick={togglePlay}
                  className="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold shadow-md flex items-center gap-2"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {isPlaying ? (
                    <>
                      <span className="text-base">⏸</span>
                      <span>Pause</span>
                    </>
                  ) : (
                    <>
                      <span className="text-base">▶</span>
                      <span>Play</span>
                    </>
                  )}
                </motion.button>

                {/* Show All / Reset */}
                <motion.button
                  onClick={handleShowAll}
                  className="px-4 py-2.5 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors font-medium"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {currentDate ? 'Show All' : 'Reset'}
                </motion.button>

                {/* Speed */}
                <motion.button
                  onClick={cycleSpeed}
                  className="px-4 py-2.5 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors font-medium"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {playSpeed}x
                </motion.button>
              </div>

              {/* Stats */}
              <div className="text-sm font-medium text-gray-600 dark:text-gray-400 hidden sm:block">
                Day {currentDayIndex + 1} of {dateRange.length}
              </div>
            </div>

            {/* Incident Distribution Graph */}
            <div>
              <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                Incident Distribution
              </div>
              <div className="h-16 flex items-end gap-0.5">
                {dateRange.map((day, idx) => {
                  const height = day.count === 0 ? 2 : Math.max(12, (day.count / Math.max(...dateRange.map(d => d.count))) * 100)
                  const isActive = idx === currentDayIndex

                  return (
                    <motion.div
                      key={idx}
                      className={`flex-1 rounded-t cursor-pointer transition-all ${
                        isActive ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-700 hover:bg-gray-400 dark:hover:bg-gray-600'
                      }`}
                      style={{ height: `${height}%` }}
                      onClick={() => {
                        setIsPlaying(false)
                        setCurrentDate(day.date)
                      }}
                      title={`${format(day.date, 'MMM d')}: ${day.count} incident${day.count !== 1 ? 's' : ''}`}
                      whileHover={{ scale: 1.02, zIndex: 10 }}
                      whileTap={{ scale: 0.98 }}
                    />
                  )
                })}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// Helper hook to calculate date range and incident counts
function useIncidentDateRange(incidents: Incident[]) {
  return {
    minDate: incidents.length > 0
      ? new Date(Math.min(...incidents.map((i) => new Date(i.occurred_at).getTime())))
      : null,
    maxDate: incidents.length > 0
      ? new Date(Math.max(...incidents.map((i) => new Date(i.occurred_at).getTime())))
      : null,
    dateRange: (() => {
      if (incidents.length === 0) return []

      const min = new Date(Math.min(...incidents.map((i) => new Date(i.occurred_at).getTime())))
      const max = new Date(Math.max(...incidents.map((i) => new Date(i.occurred_at).getTime())))

      const days: Array<{ date: Date; count: number }> = []
      const current = startOfDay(min)

      while (current <= max) {
        const dayStart = startOfDay(current)
        const dayEnd = endOfDay(current)

        const count = incidents.filter((inc) =>
          isWithinInterval(new Date(inc.occurred_at), { start: dayStart, end: dayEnd })
        ).length

        days.push({ date: new Date(dayStart), count })
        current.setDate(current.getDate() + 1)
      }

      return days
    })(),
  }
}