import type { Incident } from '@/types'
import { formatDistance } from 'date-fns/formatDistance'
import { EVIDENCE_SYSTEM } from '@/constants/evidence'

/**
 * Theme-aware color tokens for popup styling
 */
interface PopupTheme {
  textPrimary: string
  textSecondary: string
  textMuted: string
  badgeBg: string
  badgeText: string
  borderColor: string
  linkColor: string
  linkBg: string
  cardBg: string
}

/**
 * Get theme colors for popup
 */
function getPopupTheme(isDark: boolean): PopupTheme {
  return {
    textPrimary: isDark ? '#f3f4f6' : '#111827',
    textSecondary: isDark ? '#9ca3af' : '#4b5563',
    textMuted: isDark ? '#6b7280' : '#6b7280',
    badgeBg: isDark ? 'rgba(55, 65, 81, 0.8)' : 'rgba(243, 244, 246, 0.8)',
    badgeText: isDark ? '#d1d5db' : '#4b5563',
    borderColor: isDark ? 'rgba(55, 65, 81, 0.5)' : 'rgba(229, 231, 235, 0.5)',
    linkColor: isDark ? '#60a5fa' : '#2563eb',
    linkBg: isDark ? 'rgba(37, 99, 235, 0.1)' : 'rgba(37, 99, 235, 0.08)',
    cardBg: isDark ? 'rgba(55, 65, 81, 0.3)' : 'rgba(243, 244, 246, 0.5)',
  }
}

/**
 * Extract domain favicon URL
 */
function getFavicon(url: string): string {
  try {
    const domain = new URL(url).hostname
    return `https://www.google.com/s2/favicons?domain=${domain}&sz=16`
  } catch {
    return ''
  }
}

/**
 * Source type emoji mapping
 */
const SOURCE_TYPE_EMOJI: Record<string, string> = {
  'police': '🚔',
  'notam': '🛫',
  'media': '📰',
  'news': '📰',
  'social': '💬',
  'other': '🔗'
}

/**
 * Get emoji for source type
 */
function getSourceEmoji(sourceType?: string): string {
  return SOURCE_TYPE_EMOJI[sourceType?.toLowerCase() || 'other'] || '🔗'
}

/**
 * Get trust weight color
 */
function getTrustColor(trustWeight: number): string {
  if (trustWeight >= 0.8) return '#10b981'
  if (trustWeight >= 0.6) return '#f59e0b'
  return '#6b7280'
}

/**
 * Creates popup content HTML for a single incident
 *
 * @param incident - Incident data
 * @param isDark - Whether dark mode is active
 * @returns HTML string for popup content
 */
export function createPopupContent(incident: Incident, isDark: boolean = false): string {
  const timeAgo = formatDistance(new Date(incident.occurred_at), new Date(), { addSuffix: true })
  const config = EVIDENCE_SYSTEM[incident.evidence_score as 1 | 2 | 3 | 4]
  const theme = getPopupTheme(isDark)

  return `
    <div style="font-family: system-ui, -apple-system, sans-serif; padding: 4px;">
      <h3 style="margin: 0 0 10px 0; font-size: 17px; font-weight: 700; color: ${theme.textPrimary}; line-height: 1.3;">
        ${incident.title}
      </h3>

      <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 12px; flex-wrap: wrap;">
        <span style="
          background: ${config.gradient};
          color: white;
          padding: 4px 10px;
          border-radius: 14px;
          font-size: 11px;
          font-weight: 700;
          letter-spacing: 0.3px;
          text-shadow: 0 1px 2px rgba(0,0,0,0.2);
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
          ${config.label}
        </span>
        ${incident.asset_type ? `
          <span style="
            background: ${theme.badgeBg};
            color: ${theme.badgeText};
            padding: 4px 10px;
            border-radius: 14px;
            font-size: 11px;
            font-weight: 600;
            backdrop-filter: blur(10px);
            border: 1px solid ${theme.borderColor};
          ">
            ${incident.asset_type}
          </span>
        ` : ''}
        <span style="color: ${theme.textMuted}; font-size: 11px; font-weight: 500;">
          ${timeAgo}
        </span>
      </div>

      ${incident.narrative ? `
        <p style="margin: 0 0 14px 0; color: ${theme.textSecondary}; font-size: 13px; line-height: 1.6;">
          ${incident.narrative}
        </p>
      ` : ''}

      ${incident.sources && incident.sources.length > 0 ? `
        <div style="border-top: 1px solid ${theme.borderColor}; padding-top: 10px; margin-top: 8px;">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
            <div style="font-size: 11px; color: ${theme.textMuted}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
              Sources ${incident.sources.length > 1 ? `(${incident.sources.length})` : ''}
            </div>
            ${incident.sources.length >= 2 ? `
              <div style="
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
                padding: 3px 8px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: 700;
                display: inline-flex;
                align-items: center;
                gap: 4px;
              ">
                ✓ Multi-source verified
              </div>
            ` : ''}
          </div>
          <div style="display: flex; flex-direction: column; gap: 4px;">
            ${incident.sources.map(source => {
              const favicon = getFavicon(source.source_url)
              const emoji = getSourceEmoji(source.source_type)
              // Trust weight color (0-100 scale for display)
              const trustWeight = source.trust_weight || 0
              const trustColor = getTrustColor(trustWeight)
              const sourceName = source.source_title || source.source_name || source.source_type || 'Unknown'
              const showType = source.source_type && source.source_type.toLowerCase() !== sourceName.toLowerCase()

              return `
                <a href="${source.source_url}" target="_blank" rel="noopener noreferrer" style="
                  display: flex;
                  flex-direction: column;
                  gap: 2px;
                  padding: 6px 10px;
                  background: ${theme.linkBg};
                  border-radius: 10px;
                  color: ${theme.linkColor};
                  text-decoration: none;
                  transition: all 0.2s;
                  border: 1px solid ${theme.borderColor};
                  margin-bottom: 4px;
                ">
                  <div style="display: flex; align-items: center; gap: 6px;">
                    ${favicon ? `<img src="${favicon}" width="14" height="14" style="border-radius: 2px;" />` : `<span style="font-size: 14px;">${emoji}</span>`}
                    <span style="font-size: 13px; font-weight: 600;">${sourceName}</span>
                    ${trustWeight > 0 ? `
                      <span style="
                        background: ${trustColor};
                        color: white;
                        padding: 2px 6px;
                        border-radius: 8px;
                        font-size: 9px;
                        font-weight: 700;
                        margin-left: auto;
                      ">
                        ${Math.round(trustWeight * 100)}%
                      </span>
                    ` : ''}
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-left: ${trustWeight > 0 ? '2px' : 'auto'};">
                      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"/>
                    </svg>
                  </div>
                  ${showType ? `
                    <span style="font-size: 10px; color: ${theme.textMuted}; padding-left: 20px; text-transform: capitalize;">
                      ${source.source_type}
                    </span>
                  ` : ''}
                </a>
              `
            }).join('')}
          </div>
        </div>
      ` : ''}
    </div>
  `
}

/**
 * Creates popup content HTML for a facility with multiple incidents
 *
 * @param incidents - Array of incidents at this facility
 * @param facilityName - Name of the facility
 * @param emoji - Emoji representing facility type
 * @param isDark - Whether dark mode is active
 * @returns HTML string for popup content
 */
export function createFacilityPopup(
  incidents: Incident[],
  facilityName: string,
  emoji: string,
  isDark: boolean = false
): string {
  const theme = getPopupTheme(isDark)

  // Sort incidents by date (newest first)
  const sortedIncidents = [...incidents].sort((a, b) =>
    new Date(b.occurred_at).getTime() - new Date(a.occurred_at).getTime()
  )

  return `
    <div style="font-family: system-ui, -apple-system, sans-serif; padding: 4px;">
      <h3 style="margin: 0 0 10px 0; font-size: 17px; font-weight: 700; color: ${theme.textPrimary}; line-height: 1.3;">
        ${emoji} ${facilityName}
      </h3>

      <div style="margin-bottom: 12px; padding: 8px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 8px;">
        <div style="color: white; font-size: 13px; font-weight: 600; text-align: center;">
          ${incidents.length} incident${incidents.length !== 1 ? 's' : ''} at this location
        </div>
      </div>

      <div style="max-height: 300px; overflow-y: auto;">
        ${sortedIncidents.map((incident) => {
          const config = EVIDENCE_SYSTEM[incident.evidence_score as 1 | 2 | 3 | 4]
          const timeAgo = formatDistance(new Date(incident.occurred_at), new Date(), { addSuffix: true })

          return `
            <div style="
              padding: 10px;
              margin-bottom: 8px;
              border: 1px solid ${theme.borderColor};
              border-radius: 8px;
              background: ${theme.cardBg};
            ">
              <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
                <span style="
                  background: ${config.gradient};
                  color: white;
                  padding: 4px 10px;
                  border-radius: 14px;
                  font-size: 11px;
                  font-weight: 700;
                  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
                ">
                  ${config.label}
                </span>
                <span style="color: ${theme.textSecondary}; font-size: 11px; font-weight: 500;">
                  ${timeAgo}
                </span>
              </div>

              <div style="font-size: 13px; color: ${theme.textPrimary}; font-weight: 600; margin-bottom: 4px;">
                ${incident.title}
              </div>

              ${incident.narrative ? `
                <div style="font-size: 12px; color: ${theme.textSecondary}; line-height: 1.4;">
                  ${incident.narrative.substring(0, 120)}${incident.narrative.length > 120 ? '...' : ''}
                </div>
              ` : ''}
            </div>
          `
        }).join('')}
      </div>
    </div>
  `
}
