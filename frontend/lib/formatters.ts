/**
 * Formatting utilities for CEPA-style incident display
 *
 * Provides clean, readable formatting for:
 * - Location extraction and formatting
 * - Country code to full name mapping
 * - Date formatting (Month Day format)
 * - Narrative cleaning (remove Twitter handles, hashtags, URLs)
 */

import { format } from 'date-fns/format'
import type { Incident } from '@/types'

/**
 * Map ISO country codes to full country names
 */
const COUNTRY_NAMES: Record<string, string> = {
  // Nordic Countries
  'DK': 'Denmark',
  'SE': 'Sweden',
  'NO': 'Norway',
  'FI': 'Finland',
  'IS': 'Iceland',

  // Baltic Countries
  'EE': 'Estonia',
  'LV': 'Latvia',
  'LT': 'Lithuania',

  // Western Europe
  'BE': 'Belgium',
  'NL': 'Netherlands',
  'LU': 'Luxembourg',
  'FR': 'France',
  'DE': 'Germany',
  'AT': 'Austria',
  'CH': 'Switzerland',
  'LI': 'Liechtenstein',

  // British Isles
  'GB': 'United Kingdom',
  'UK': 'United Kingdom',
  'IE': 'Ireland',

  // Southern Europe
  'ES': 'Spain',
  'PT': 'Portugal',
  'IT': 'Italy',
  'MT': 'Malta',
  'GR': 'Greece',
  'CY': 'Cyprus',

  // Central Europe
  'PL': 'Poland',
  'CZ': 'Czech Republic',
  'SK': 'Slovakia',
  'HU': 'Hungary',
  'SI': 'Slovenia',
  'HR': 'Croatia',

  // Eastern Europe (EU members)
  'RO': 'Romania',
  'BG': 'Bulgaria',

  // Southeastern Europe
  'AL': 'Albania',
  'BA': 'Bosnia and Herzegovina',
  'ME': 'Montenegro',
  'MK': 'North Macedonia',
  'RS': 'Serbia',
  'XK': 'Kosovo',
}

/**
 * Extract location (city/area) from incident data
 *
 * Attempts to extract location in this order:
 * 1. Use location_name if available
 * 2. Parse city from title (e.g., "Drone spotted over Copenhagen" → "Copenhagen")
 * 3. Parse city from narrative
 * 4. Fallback to asset type + country (e.g., "Airport, Denmark")
 *
 * @param incident - Incident object
 * @returns Clean location string (city name or area)
 */
export function extractLocation(incident: Incident): string {
  // Use location_name if available
  if (incident.location_name) {
    return incident.location_name
  }

  const searchText = `${incident.title} ${incident.narrative || ''}`

  // Filter out generic/noise words that shouldn't be locations
  const noiseWords = /^(unidentified|drone|drones|unknown|spotted|sighting|incident|activity)$/i

  // Common location patterns in titles and narratives
  const locationPatterns = [
    // "Drone spotted over Copenhagen" → "Copenhagen"
    /(?:over|near|at|in|around)\s+([A-Z][a-zA-Z\s-]+?)(?:\s+(?:airport|airbase|harbor|port|bridge|area|region)|\s*[,.]|$)/i,

    // "Copenhagen Airport" → "Copenhagen"
    /^([A-Z][a-zA-Z\s-]+?)\s+(?:Airport|Airbase|Harbor|Port|Bridge)/i,

    // "COPENHAGEN airspace" → "Copenhagen"
    /^([A-Z]+)\s+(?:airspace|area|region|zone)/i,
  ]

  for (const pattern of locationPatterns) {
    const match = searchText.match(pattern)
    if (match && match[1]) {
      // Clean up the extracted location
      let location = match[1].trim()

      // Skip if it's a noise word
      if (noiseWords.test(location)) {
        continue
      }

      // Remove common noise words
      location = location.replace(/\b(the|a|an|at|in|on|near)\b/gi, '').trim()

      // Capitalize properly (handle "COPENHAGEN" → "Copenhagen")
      if (location === location.toUpperCase() && location.length > 3) {
        location = location.charAt(0) + location.slice(1).toLowerCase()
      }

      if (location && location.length > 2 && !noiseWords.test(location)) {
        return location
      }
    }
  }

  // Fallback: use asset type as location descriptor
  if (incident.asset_type) {
    const assetNames: Record<string, string> = {
      'airport': 'Airport',
      'military': 'Military Base',
      'harbor': 'Harbor',
      'powerplant': 'Power Plant',
      'bridge': 'Bridge',
      'other': 'Area'
    }
    return assetNames[incident.asset_type] || 'Unknown Location'
  }

  return 'Unknown Location'
}

/**
 * Format ISO country code to full country name
 *
 * @param code - ISO 3166-1 alpha-2 country code (e.g., "DK", "SE")
 * @returns Full country name (e.g., "Denmark", "Sweden")
 */
export function formatCountry(code: string): string {
  if (!code) return 'Unknown Country'

  const upperCode = code.toUpperCase()
  return COUNTRY_NAMES[upperCode] || code
}

/**
 * Format incident date to CEPA-style format
 *
 * Formats as:
 * - "September 10" for current year incidents
 * - "September 10, 2024" for past year incidents
 *
 * @param isoDate - ISO 8601 date string
 * @returns Formatted date string
 */
export function formatIncidentDate(isoDate: string): string {
  if (!isoDate) return 'Unknown Date'

  try {
    const date = new Date(isoDate)
    const currentYear = new Date().getFullYear()
    const incidentYear = date.getFullYear()

    // Use "Month Day" for current year, "Month Day, Year" for past years
    if (incidentYear === currentYear) {
      return format(date, 'MMMM d')
    } else {
      return format(date, 'MMMM d, yyyy')
    }
  } catch (error) {
    return 'Unknown Date'
  }
}

/**
 * Clean narrative text for CEPA-style display
 *
 * Removes:
 * - Twitter handles (@username)
 * - Hashtags (#politidk)
 * - URLs (http://... or https://...)
 * - Extra whitespace
 * - RSS artifacts
 *
 * @param text - Raw narrative text
 * @returns Clean, readable narrative
 */
export function cleanNarrative(text: string): string {
  if (!text) return ''

  let cleaned = text

  // Remove URLs (http/https)
  cleaned = cleaned.replace(/https?:\/\/[^\s]+/gi, '')

  // Remove email addresses FIRST (before removing @ symbols)
  cleaned = cleaned.replace(/\S+@\S+\.\S+/g, '')

  // Remove Twitter handles (@username)
  cleaned = cleaned.replace(/@[\w]+/g, '')

  // Remove hashtags (#politidk)
  cleaned = cleaned.replace(/#[\w]+/g, '')

  // Remove extra whitespace and normalize
  cleaned = cleaned.replace(/\s+/g, ' ').trim()

  // Remove leading/trailing punctuation artifacts (but preserve final periods)
  cleaned = cleaned.replace(/^[,\-:;\s]+/, '')

  return cleaned
}

/**
 * Format complete CEPA-style location string
 *
 * Combines city/location with country name
 *
 * @param incident - Incident object
 * @returns Formatted location string (e.g., "Copenhagen, Denmark")
 */
export function formatLocation(incident: Incident): string {
  const city = extractLocation(incident)
  const country = formatCountry(incident.country)

  return `${city}, ${country}`
}

/**
 * Get shortened narrative for compact display (popups)
 *
 * Limits to first 2-3 sentences or ~200 characters
 *
 * @param narrative - Full narrative text
 * @param maxLength - Maximum character length (default: 200)
 * @returns Shortened narrative with ellipsis if truncated
 */
export function getShortNarrative(narrative: string, maxLength: number = 200): string {
  const cleaned = cleanNarrative(narrative)

  if (!cleaned) return ''

  // Try to split by sentences (. ! ?)
  const sentences = cleaned.split(/[.!?]+/).filter(s => s.trim().length > 0)

  // Take first 2-3 sentences and join with single space + period
  let result = sentences.slice(0, 3).map(s => s.trim()).join('. ')

  // Add period if doesn't have one
  if (!result.endsWith('.') && !result.endsWith('!') && !result.endsWith('?')) {
    result += '.'
  }

  // If already short enough, return as-is
  if (result.length <= maxLength) {
    return result
  }

  // If still too long, truncate at word boundary
  result = result.substring(0, maxLength)
  const lastSpace = result.lastIndexOf(' ')
  if (lastSpace > maxLength * 0.8) {
    result = result.substring(0, lastSpace)
  }
  result += '...'

  return result
}
