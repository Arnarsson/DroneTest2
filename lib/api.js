// DroneWatch API Client
// This file provides a clean interface to fetch incidents from either the FastAPI backend or Supabase directly

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Fetch incidents from the FastAPI backend
 * @param {Object} params - Query parameters
 * @param {number} params.minEvidence - Minimum evidence score (1-4)
 * @param {string} params.country - Country code (e.g., 'DK')
 * @param {number} params.limit - Maximum number of results
 * @param {number} params.offset - Pagination offset
 * @param {string} params.bbox - Bounding box (minLon,minLat,maxLon,maxLat)
 * @param {string} params.since - ISO datetime string
 * @param {string} params.until - ISO datetime string
 * @returns {Promise<Array>} Array of incidents
 */
export async function fetchIncidents(params = {}) {
  const queryParams = new URLSearchParams();

  // Add parameters if provided
  if (params.minEvidence) queryParams.append('min_evidence', params.minEvidence);
  if (params.country) queryParams.append('country', params.country);
  if (params.limit) queryParams.append('limit', params.limit);
  if (params.offset) queryParams.append('offset', params.offset);
  if (params.bbox) queryParams.append('bbox', params.bbox);
  if (params.since) queryParams.append('since', params.since);
  if (params.until) queryParams.append('until', params.until);
  if (params.assetType) queryParams.append('asset_type', params.assetType);
  if (params.status) queryParams.append('status', params.status);

  try {
    const response = await fetch(`${API_BASE}/incidents?${queryParams.toString()}`);
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch incidents:', error);
    throw error;
  }
}

/**
 * Fetch a single incident by ID
 * @param {string} id - Incident UUID
 * @returns {Promise<Object>} Incident details with sources
 */
export async function fetchIncidentById(id) {
  try {
    const response = await fetch(`${API_BASE}/incidents/${id}`);
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch incident:', error);
    throw error;
  }
}

/**
 * Get embed snippet HTML
 * @param {Object} params - Embed parameters
 * @returns {Promise<string>} HTML iframe snippet
 */
export async function getEmbedSnippet(params = {}) {
  const queryParams = new URLSearchParams();
  if (params.minEvidence) queryParams.append('min_evidence', params.minEvidence);
  if (params.country) queryParams.append('country', params.country);
  if (params.height) queryParams.append('height', params.height);

  try {
    const response = await fetch(`${API_BASE}/embed/snippet?${queryParams.toString()}`);
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    return await response.text();
  } catch (error) {
    console.error('Failed to get embed snippet:', error);
    throw error;
  }
}

/**
 * Helper to format evidence score as text
 * @param {number} score - Evidence score (1-4)
 * @returns {string} Human-readable evidence level
 */
export function formatEvidenceLevel(score) {
  const levels = {
    4: 'Official',
    3: 'Verified Media',
    2: 'OSINT',
    1: 'Unverified'
  };
  return levels[score] || 'Unknown';
}

/**
 * Helper to format incident date
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
 */
export function formatIncidentDate(dateString) {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short'
  }).format(date);
}

// Export Denmark bounding box for convenience
export const DENMARK_BBOX = '7.7,54.4,15.5,57.8';
export const NORDICS_BBOX = '4.0,54.0,32.0,71.5';