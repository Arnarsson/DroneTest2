'use client'

import type { Incident } from '@/types'
import {
  formatIncidentsToCSV,
  formatIncidentsToJSON,
  downloadFile,
  generateExportFilename,
} from '@/lib/export'

interface ExportButtonsProps {
  incidents: Incident[]
  isDisabled?: boolean
}

/**
 * Download icon SVG component for export buttons
 */
function DownloadIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
      />
    </svg>
  )
}

/**
 * Export buttons component for downloading incidents in CSV or JSON format
 *
 * Renders two buttons that trigger file downloads with timestamped filenames.
 * Styling matches the existing "Group by Facility" toggle button.
 */
export function ExportButtons({ incidents, isDisabled = false }: ExportButtonsProps) {
  const handleExportCSV = () => {
    if (isDisabled || incidents.length === 0) return

    const csvContent = formatIncidentsToCSV(incidents)
    const filename = generateExportFilename('csv')
    downloadFile(csvContent, filename, 'text/csv')
  }

  const handleExportJSON = () => {
    if (isDisabled || incidents.length === 0) return

    const jsonContent = formatIncidentsToJSON(incidents)
    const filename = generateExportFilename('json')
    downloadFile(jsonContent, filename, 'application/json')
  }

  const buttonBaseClasses = 'flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all focus-ring'
  const buttonEnabledClasses = 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
  const buttonDisabledClasses = 'bg-gray-100 dark:bg-gray-800 text-gray-400 dark:text-gray-600 cursor-not-allowed opacity-50'

  const buttonClasses = `${buttonBaseClasses} ${isDisabled ? buttonDisabledClasses : buttonEnabledClasses}`

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={handleExportCSV}
        disabled={isDisabled}
        className={buttonClasses}
        aria-label="Export incidents to CSV"
        title="Export incidents to CSV"
      >
        <DownloadIcon className="w-4 h-4" />
        Export CSV
      </button>
      <button
        onClick={handleExportJSON}
        disabled={isDisabled}
        className={buttonClasses}
        aria-label="Export incidents to JSON"
        title="Export incidents to JSON"
      >
        <DownloadIcon className="w-4 h-4" />
        Export JSON
      </button>
    </div>
  )
}
