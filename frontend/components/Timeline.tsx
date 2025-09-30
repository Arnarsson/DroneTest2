'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
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

  // Initialize current date to earliest incident
  useEffect(() => {
    if (minDate && !currentDate) {
      setCurrentDate(minDate)
    }
  }, [minDate, currentDate])

  // Handle animation playback
  useEffect(() => {
    if (!isPlaying || !currentDate || !maxDate) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
      return
    }

    // Move forward one day every interval based on speed
    const intervalMs = 1000 / playSpeed
    intervalRef.current = setInterval(() => {
      setCurrentDate((prev) => {
        if (!prev || !maxDate) return prev

        const nextDate = new Date(prev)
        nextDate.setDate(nextDate.getDate() + 1)

        // Stop at end
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
    setCurrentDate(minDate)
  }, [minDate])

  const handleDateChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setIsPlaying(false)
    const dayIndex = parseInt(e.target.value)
    if (dateRange[dayIndex]) {
      setCurrentDate(dateRange[dayIndex].date)
    }
  }, [dateRange])

  const togglePlay = useCallback(() => {
    setIsPlaying((prev) => !prev)
  }, [])

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
    <div className="bg-white border-t border-gray-200 shadow-lg">
      {/* Toggle Button */}
      <button
        onClick={onToggle}
        className="w-full px-4 py-2 flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className="text-lg">⏱️</span>
          <span className="font-medium text-gray-900">Timeline</span>
          {currentDate && (
            <span className="text-sm text-gray-500">
              {format(currentDate, 'MMM d, yyyy')} • {incidentsOnCurrentDay.length} incident{incidentsOnCurrentDay.length !== 1 ? 's' : ''}
            </span>
          )}
        </div>
        <svg
          className={`w-5 h-5 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Timeline Controls */}
      {isOpen && (
        <div className="px-4 pb-4 space-y-4">
          {/* Slider */}
          <div className="relative">
            <input
              type="range"
              min={0}
              max={dateRange.length - 1}
              value={currentDayIndex}
              onChange={handleDateChange}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
              style={{
                background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${(currentDayIndex / (dateRange.length - 1)) * 100}%, #e5e7eb ${(currentDayIndex / (dateRange.length - 1)) * 100}%, #e5e7eb 100%)`
              }}
            />

            {/* Date markers */}
            <div className="flex justify-between mt-2 text-xs text-gray-500">
              <span>{format(minDate, 'MMM d')}</span>
              <span>{format(maxDate, 'MMM d')}</span>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {/* Play/Pause */}
              <button
                onClick={togglePlay}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                {isPlaying ? '⏸ Pause' : '▶ Play'}
              </button>

              {/* Reset */}
              <button
                onClick={handleReset}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
              >
                ↺ Reset
              </button>

              {/* Speed */}
              <button
                onClick={cycleSpeed}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
              >
                {playSpeed}x Speed
              </button>
            </div>

            {/* Stats */}
            <div className="text-sm text-gray-600">
              Day {currentDayIndex + 1} of {dateRange.length}
            </div>
          </div>

          {/* Incident Distribution Graph */}
          <div className="h-12 flex items-end gap-0.5">
            {dateRange.map((day, idx) => {
              const height = day.count === 0 ? 2 : Math.max(8, (day.count / Math.max(...dateRange.map(d => d.count))) * 100)
              const isActive = idx === currentDayIndex

              return (
                <div
                  key={idx}
                  className={`flex-1 rounded-t transition-all cursor-pointer ${
                    isActive ? 'bg-blue-600' : 'bg-gray-300 hover:bg-gray-400'
                  }`}
                  style={{ height: `${height}%` }}
                  onClick={() => {
                    setIsPlaying(false)
                    setCurrentDate(day.date)
                  }}
                  title={`${format(day.date, 'MMM d')}: ${day.count} incident${day.count !== 1 ? 's' : ''}`}
                />
              )
            })}
          </div>
        </div>
      )}
    </div>
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