/**
 * URL Filter Parameter Utilities
 *
 * Provides type-safe parsing and serialization of filter state
 * for URL query parameters. Handles validation and falls back
 * to defaults for invalid/malicious input.
 */

import type { FilterState } from '@/types'

/**
 * Default filter values used when URL params are missing or invalid
 */
export const DEFAULT_FILTER_STATE: FilterState = {
  minEvidence: 1,
  country: 'all',
  status: 'all',
  assetType: null,
  dateRange: 'all',
  searchQuery: '',
}

/**
 * Valid values for dateRange filter
 */
export const VALID_DATE_RANGES = ['day', 'week', 'month', 'all'] as const

/**
 * Valid values for minEvidence filter
 */
export const MIN_EVIDENCE_RANGE = { min: 1, max: 4 } as const

/**
 * URL parameter key mapping (snake_case to match API conventions)
 */
export const URL_PARAM_KEYS = {
  minEvidence: 'min_evidence',
  country: 'country',
  status: 'status',
  assetType: 'asset_type',
  dateRange: 'date_range',
  searchQuery: 'search',
} as const

/**
 * Parse and validate minEvidence value from URL
 * Valid range is 1-4, defaults to 1 if invalid
 *
 * @param value - Raw string value from URL parameter
 * @returns Validated minEvidence number (1-4)
 */
export function parseMinEvidence(value: string | null): number {
  if (!value) return DEFAULT_FILTER_STATE.minEvidence

  // Trim whitespace and handle empty strings
  const trimmed = value.trim()
  if (!trimmed) return DEFAULT_FILTER_STATE.minEvidence

  const parsed = parseInt(trimmed, 10)

  // Check for NaN or non-integer values
  if (isNaN(parsed) || !Number.isInteger(parsed)) {
    return DEFAULT_FILTER_STATE.minEvidence
  }

  // Clamp to valid range
  if (parsed < MIN_EVIDENCE_RANGE.min || parsed > MIN_EVIDENCE_RANGE.max) {
    return DEFAULT_FILTER_STATE.minEvidence
  }

  return parsed
}

/**
 * Parse and validate dateRange value from URL
 * Must be one of: 'day', 'week', 'month', 'all'
 *
 * @param value - Raw string value from URL parameter
 * @returns Validated dateRange value
 */
export function parseDateRange(value: string | null): FilterState['dateRange'] {
  if (!value) return DEFAULT_FILTER_STATE.dateRange

  // Trim and normalize to lowercase for comparison
  const trimmed = value.trim().toLowerCase()
  if (!trimmed) return DEFAULT_FILTER_STATE.dateRange

  // Type guard check against valid values
  if (VALID_DATE_RANGES.includes(trimmed as FilterState['dateRange'])) {
    return trimmed as FilterState['dateRange']
  }

  return DEFAULT_FILTER_STATE.dateRange
}

/**
 * Parse assetType from URL (can be null)
 * Handles various representations of null/empty values
 *
 * @param value - Raw string value from URL parameter
 * @returns Asset type string or null
 */
export function parseAssetType(value: string | null): string | null {
  if (!value) return null

  const trimmed = value.trim()

  // Handle explicit null representations
  if (
    !trimmed ||
    trimmed === 'null' ||
    trimmed === 'undefined' ||
    trimmed === 'none'
  ) {
    return null
  }

  return trimmed
}

/**
 * Parse and validate country value from URL
 * Returns default if empty or contains only whitespace
 *
 * @param value - Raw string value from URL parameter
 * @returns Country string (uppercase if valid code, or 'all')
 */
export function parseCountry(value: string | null): string {
  if (!value) return DEFAULT_FILTER_STATE.country

  const trimmed = value.trim()
  if (!trimmed) return DEFAULT_FILTER_STATE.country

  return trimmed
}

/**
 * Parse and validate status value from URL
 * Returns default if empty or contains only whitespace
 *
 * @param value - Raw string value from URL parameter
 * @returns Status string
 */
export function parseStatus(value: string | null): string {
  if (!value) return DEFAULT_FILTER_STATE.status

  const trimmed = value.trim()
  if (!trimmed) return DEFAULT_FILTER_STATE.status

  return trimmed
}

/**
 * Parse filter state from URL search params
 * Validates all parameters and falls back to defaults for invalid values
 *
 * @param searchParams - URLSearchParams object from URL
 * @returns Validated FilterState object
 *
 * @example
 * ```ts
 * const params = new URLSearchParams('?country=DK&min_evidence=3')
 * const filters = parseFilterParams(params)
 * // { country: 'DK', minEvidence: 3, status: 'all', assetType: null, dateRange: 'all', searchQuery: '' }
 * ```
 */
export function parseFilterParams(searchParams: URLSearchParams): FilterState {
  return {
    minEvidence: parseMinEvidence(searchParams.get(URL_PARAM_KEYS.minEvidence)),
    country: parseCountry(searchParams.get(URL_PARAM_KEYS.country)),
    status: parseStatus(searchParams.get(URL_PARAM_KEYS.status)),
    assetType: parseAssetType(searchParams.get(URL_PARAM_KEYS.assetType)),
    dateRange: parseDateRange(searchParams.get(URL_PARAM_KEYS.dateRange)),
    searchQuery: searchParams.get(URL_PARAM_KEYS.searchQuery) || '',
  }
}

/**
 * Serialize filter state to URL search params
 * Only includes non-default values to keep URLs clean
 *
 * @param filters - FilterState object to serialize
 * @returns URLSearchParams object with only non-default values
 *
 * @example
 * ```ts
 * const params = serializeFilterParams({
 *   country: 'DK',
 *   minEvidence: 3,
 *   status: 'all',
 *   assetType: null,
 *   dateRange: 'week'
 * })
 * // params.toString() => 'country=DK&min_evidence=3&date_range=week'
 * ```
 */
export function serializeFilterParams(filters: FilterState): URLSearchParams {
  const params = new URLSearchParams()

  // Only add params that differ from defaults to keep URLs clean
  if (filters.minEvidence !== DEFAULT_FILTER_STATE.minEvidence) {
    params.set(URL_PARAM_KEYS.minEvidence, filters.minEvidence.toString())
  }

  if (filters.country !== DEFAULT_FILTER_STATE.country) {
    params.set(URL_PARAM_KEYS.country, filters.country)
  }

  if (filters.status !== DEFAULT_FILTER_STATE.status) {
    params.set(URL_PARAM_KEYS.status, filters.status)
  }

  if (filters.assetType !== DEFAULT_FILTER_STATE.assetType && filters.assetType !== null) {
    params.set(URL_PARAM_KEYS.assetType, filters.assetType)
  }

  if (filters.dateRange !== DEFAULT_FILTER_STATE.dateRange) {
    params.set(URL_PARAM_KEYS.dateRange, filters.dateRange)
  }

  if (filters.searchQuery && filters.searchQuery.trim() !== '') {
    params.set(URL_PARAM_KEYS.searchQuery, filters.searchQuery)
  }

  return params
}
