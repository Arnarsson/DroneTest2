/**
 * Export utilities for DroneWatch incidents
 *
 * Provides functions for exporting incident data in CSV and JSON formats
 * with proper formatting and file download capabilities.
 *
 * Usage:
 * import { formatIncidentsToCSV, formatIncidentsToJSON, downloadFile } from '@/lib/export'
 *
 * const csvData = formatIncidentsToCSV(incidents)
 * downloadFile(csvData, 'incidents.csv', 'text/csv')
 */

import type { Incident } from '@/types'
import { formatCountry, extractLocation, cleanNarrative, formatIncidentDate } from './formatters'

/**
 * CSV column headers for incident export
 */
const CSV_HEADERS = [
  'Title',
  'Date',
  'Location',
  'Country',
  'Evidence Score',
  'Sources Count',
  'Narrative',
]

/**
 * Escape a value for CSV format
 *
 * Handles:
 * - Values containing commas, quotes, or newlines
 * - Values with double quotes (escaped as "")
 *
 * @param value - The value to escape
 * @returns Properly escaped CSV value
 */
function escapeCSVValue(value: string | number): string {
  const stringValue = String(value)

  // If the value contains commas, quotes, or newlines, wrap in quotes
  if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n') || stringValue.includes('\r')) {
    // Escape internal quotes by doubling them
    const escaped = stringValue.replace(/"/g, '""')
    return `"${escaped}"`
  }

  return stringValue
}

/**
 * Format an array of incidents to CSV string
 *
 * Includes headers: Title, Date, Location, Country, Evidence Score, Sources Count, Narrative
 * Uses existing formatters for consistent data display.
 *
 * @param incidents - Array of incidents to export
 * @returns CSV formatted string with headers
 */
export function formatIncidentsToCSV(incidents: Incident[]): string {
  // Start with headers
  const lines: string[] = [CSV_HEADERS.join(',')]

  for (const incident of incidents) {
    const row = [
      escapeCSVValue(incident.title),
      escapeCSVValue(formatIncidentDate(incident.occurred_at)),
      escapeCSVValue(extractLocation(incident)),
      escapeCSVValue(formatCountry(incident.country)),
      escapeCSVValue(incident.evidence_score),
      escapeCSVValue(incident.sources?.length ?? 0),
      escapeCSVValue(cleanNarrative(incident.narrative || '')),
    ]
    lines.push(row.join(','))
  }

  return lines.join('\n')
}

/**
 * Export data structure for JSON format
 */
interface ExportedIncident {
  title: string
  date: string
  location: string
  country: string
  evidenceScore: number
  sourcesCount: number
  narrative: string
  coordinates: {
    lat: number
    lon: number
  }
  sources: Array<{
    title?: string
    url: string
    type: string
  }>
}

/**
 * Format an array of incidents to clean JSON
 *
 * Exports relevant fields with clean formatting:
 * - title, date, location, country, evidenceScore, sourcesCount
 * - narrative (cleaned)
 * - coordinates (lat, lon)
 * - sources (title, url, type)
 *
 * @param incidents - Array of incidents to export
 * @returns JSON formatted string
 */
export function formatIncidentsToJSON(incidents: Incident[]): string {
  const exportedIncidents: ExportedIncident[] = incidents.map((incident) => ({
    title: incident.title,
    date: formatIncidentDate(incident.occurred_at),
    location: extractLocation(incident),
    country: formatCountry(incident.country),
    evidenceScore: incident.evidence_score,
    sourcesCount: incident.sources?.length ?? 0,
    narrative: cleanNarrative(incident.narrative || ''),
    coordinates: {
      lat: incident.lat,
      lon: incident.lon,
    },
    sources: (incident.sources || []).map((source) => ({
      title: source.source_title,
      url: source.source_url,
      type: source.source_type,
    })),
  }))

  return JSON.stringify(exportedIncidents, null, 2)
}

/**
 * Trigger a file download in the browser
 *
 * Creates a Blob from the content and triggers a download using
 * URL.createObjectURL. Cleans up the object URL after download.
 *
 * @param content - The file content to download
 * @param filename - The name for the downloaded file
 * @param mimeType - The MIME type of the file (e.g., 'text/csv', 'application/json')
 */
export function downloadFile(content: string, filename: string, mimeType: string): void {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)

  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.style.display = 'none'

  document.body.appendChild(link)
  link.click()

  // Clean up
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

/**
 * Generate a timestamped filename for exports
 *
 * Format: dronewatch-incidents-YYYY-MM-DD.{extension}
 *
 * @param extension - File extension (e.g., 'csv', 'json')
 * @returns Formatted filename with current date
 */
export function generateExportFilename(extension: string): string {
  const date = new Date()
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')

  return `dronewatch-incidents-${year}-${month}-${day}.${extension}`
}
