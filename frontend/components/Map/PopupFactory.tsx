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
 * Source type emoji mapping based on trust weight
 */
const SOURCE_TYPE_EMOJI: Record<string, string> = {
  'police': '🚨',
  'military': '🚨',
  'aviation_authority': '🚨',
  'notam': '🚨',
  'verified_media': '📰',
  'media': '📄',
  'news': '📄',
  'social': '📱',
  'other': '🔗'
}

/**
 * Get emoji for source based on trust weight and type
 */
function getSourceEmoji(trustWeight: number, sourceType?: string): string {
  // Authority-based emoji selection (overrides type)
  if (trustWeight >= 4) return '🚨'  // Police/Official
  if (trustWeight >= 3) return '📰'  // Verified Media
  if (trustWeight >= 2) return '📄'  // Media
  if (trustWeight >= 1) return '📱'  // Social/Low Trust

  // Fallback to type-based emoji
  return SOURCE_TYPE_EMOJI[sourceType?.toLowerCase() || 'other'] || '🔗'
}

/**
 * Get trust weight color and border based on authority level
 */
function getTrustStyles(trustWeight: number): { bgClass: string; borderClass: string; textClass: string } {
  if (trustWeight >= 4) return {
    bgClass: 'bg-green-50 dark:bg-green-900/20',
    borderClass: 'border-green-500',
    textClass: 'text-green-900 dark:text-green-100'
  }
  if (trustWeight >= 3) return {
    bgClass: 'bg-amber-50 dark:bg-amber-900/20',
    borderClass: 'border-amber-500',
    textClass: 'text-amber-900 dark:text-amber-100'
  }
  if (trustWeight >= 2) return {
    bgClass: 'bg-orange-50 dark:bg-orange-900/20',
    borderClass: 'border-orange-500',
    textClass: 'text-orange-900 dark:text-orange-100'
  }
  return {
    bgClass: 'bg-red-50 dark:bg-red-900/20',
    borderClass: 'border-red-500',
    textClass: 'text-red-900 dark:text-red-100'
  }
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
        <div style="border-top: 1px solid ${theme.borderColor}; padding-top: 12px; margin-top: 12px;">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
            <div style="font-size: 12px; color: ${theme.textMuted}; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
              ${incident.sources.length === 1 ? 'Source' : `Sources (${incident.sources.length})`}
            </div>
            ${incident.sources.some((s: any) => s.trust_weight >= 4) ? `
              <div style="
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
                padding: 4px 10px;
                border-radius: 14px;
                font-size: 10px;
                font-weight: 700;
                display: inline-flex;
                align-items: center;
                gap: 4px;
                box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
              ">
                🚨 Official Source
              </div>
            ` : incident.sources.length >= 2 ? `
              <div style="
                background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
                color: white;
                padding: 4px 10px;
                border-radius: 14px;
                font-size: 10px;
                font-weight: 700;
                display: inline-flex;
                align-items: center;
                gap: 4px;
                box-shadow: 0 2px 4px rgba(245, 158, 11, 0.3);
              ">
                ✓ Multi-source verified
              </div>
            ` : ''}
          </div>
          <div style="display: flex; flex-direction: column; gap: 8px;">
            ${[...incident.sources]
              .sort((a: any, b: any) => (b.trust_weight || 0) - (a.trust_weight || 0))
              .map((source: any) => {
                const trustWeight = source.trust_weight || 0
                const emoji = getSourceEmoji(trustWeight, source.source_type)
                const sourceName = source.source_title || source.source_name || source.source_type || 'Unknown Source'
                const showType = source.source_type && source.source_type.toLowerCase() !== sourceName.toLowerCase()

                // Inline styling based on trust weight
                let borderColor = '#ef4444'  // red-500
                let bgColor = isDark ? 'rgba(239, 68, 68, 0.1)' : 'rgba(254, 242, 242, 0.8)'
                let authorityLabel = ''

                if (trustWeight >= 4) {
                  borderColor = '#10b981'  // green-500
                  bgColor = isDark ? 'rgba(16, 185, 129, 0.15)' : 'rgba(236, 253, 245, 0.9)'
                  authorityLabel = 'Official/Police Source'
                } else if (trustWeight >= 3) {
                  borderColor = '#f59e0b'  // amber-500
                  bgColor = isDark ? 'rgba(245, 158, 11, 0.15)' : 'rgba(255, 251, 235, 0.9)'
                  authorityLabel = 'Verified Media'
                } else if (trustWeight >= 2) {
                  borderColor = '#f97316'  // orange-500
                  bgColor = isDark ? 'rgba(249, 115, 22, 0.15)' : 'rgba(255, 247, 237, 0.9)'
                  authorityLabel = 'News Media'
                } else {
                  authorityLabel = 'Low Trust Source'
                }

                return `
                  <div style="
                    padding: 10px;
                    background: ${bgColor};
                    border: 2px solid ${borderColor};
                    border-radius: 10px;
                    transition: all 0.2s ease;
                  ">
                    <div style="display: flex; align-items: start; gap: 8px; margin-bottom: 6px;">
                      <span style="font-size: 20px; line-height: 1; flex-shrink: 0;">${emoji}</span>
                      <div style="flex: 1; min-width: 0;">
                        <a href="${source.source_url}" target="_blank" rel="noopener noreferrer" style="
                          color: ${theme.linkColor};
                          font-size: 13px;
                          font-weight: 600;
                          text-decoration: none;
                          word-break: break-word;
                          display: flex;
                          align-items: center;
                          gap: 4px;
                        ">
                          ${sourceName}
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex-shrink: 0;">
                            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"/>
                          </svg>
                        </a>
                        <div style="
                          font-size: 10px;
                          color: ${theme.textMuted};
                          margin-top: 2px;
                          font-weight: 600;
                          text-transform: uppercase;
                          letter-spacing: 0.3px;
                        ">
                          ${authorityLabel}${showType ? ` • ${source.source_type}` : ''}
                        </div>
                      </div>
                    </div>
                    ${source.source_quote ? `
                      <blockquote style="
                        margin: 6px 0 0 28px;
                        padding: 6px 10px;
                        background: ${isDark ? 'rgba(0, 0, 0, 0.2)' : 'rgba(255, 255, 255, 0.6)'};
                        border-left: 3px solid ${borderColor};
                        border-radius: 4px;
                        font-size: 11px;
                        font-style: italic;
                        color: ${theme.textSecondary};
                        line-height: 1.5;
                      ">
                        "${source.source_quote.substring(0, 150)}${source.source_quote.length > 150 ? '...' : ''}"
                      </blockquote>
                    ` : ''}
                  </div>
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
