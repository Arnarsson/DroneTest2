'use client'

import { motion } from 'framer-motion'

interface SourceBadgeProps {
  url: string
  type?: string
  title?: string
  className?: string
}

export function SourceBadge({ url, type = 'other', title, className = '' }: SourceBadgeProps) {
  const getFavicon = (url: string) => {
    try {
      const domain = new URL(url).hostname
      return `https://www.google.com/s2/favicons?domain=${domain}&sz=16`
    } catch {
      return null
    }
  }

  const getDomain = (url: string) => {
    try {
      // Validate URL is real (not test/placeholder)
      const urlLower = url.toLowerCase()
      const blockedPatterns = ['test', 'example', 'localhost', 'placeholder', 'dummy', 'fake']
      if (blockedPatterns.some(pattern => urlLower.includes(pattern))) {
        console.warn(`[SourceBadge] Suspicious URL detected: ${url}`)
      }
      
      return new URL(url).hostname.replace('www.', '')
    } catch {
      console.error(`[SourceBadge] Invalid URL: ${url}`)
      return 'Invalid Source'
    }
  }

  const typeConfig: Record<string, { emoji: string; color: string; hoverColor: string }> = {
    police: {
      emoji: '🚔',
      color: 'bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-300 border-green-200 dark:border-green-800',
      hoverColor: 'hover:bg-green-100 dark:hover:bg-green-900/50'
    },
    notam: {
      emoji: '🛫',
      color: 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800',
      hoverColor: 'hover:bg-blue-100 dark:hover:bg-blue-900/50'
    },
    media: {
      emoji: '📰',
      color: 'bg-yellow-50 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 border-yellow-200 dark:border-yellow-800',
      hoverColor: 'hover:bg-yellow-100 dark:hover:bg-yellow-900/50'
    },
    news: {
      emoji: '📰',
      color: 'bg-yellow-50 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 border-yellow-200 dark:border-yellow-800',
      hoverColor: 'hover:bg-yellow-100 dark:hover:bg-yellow-900/50'
    },
    social: {
      emoji: '💬',
      color: 'bg-orange-50 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 border-orange-200 dark:border-orange-800',
      hoverColor: 'hover:bg-orange-100 dark:hover:bg-orange-900/50'
    },
    other: {
      emoji: '🔗',
      color: 'bg-gray-50 dark:bg-gray-800/50 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-700',
      hoverColor: 'hover:bg-gray-100 dark:hover:bg-gray-800'
    }
  }

  const config = typeConfig[type.toLowerCase()] || typeConfig.other
  const favicon = getFavicon(url)
  const domain = getDomain(url)

  return (
    <div className="relative group inline-block">
      <motion.a
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className={`inline-flex items-center gap-2 text-xs font-semibold px-3 py-2 rounded-lg border transition-all focus-ring ${config.color} ${config.hoverColor} ${className}`}
        whileHover={{ scale: 1.03, y: -2 }}
        whileTap={{ scale: 0.98 }}
        aria-label={`View source: ${title || domain}`}
      >
        {favicon ? (
          <img
            src={favicon}
            alt=""
            width={14}
            height={14}
            className="rounded-sm"
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = 'none'
            }}
          />
        ) : (
          <span className="text-sm">{config.emoji}</span>
        )}
        <span className="max-w-[120px] truncate">{title || domain}</span>
        <svg className="w-3 h-3 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
        </svg>
      </motion.a>

      {/* Tooltip with full URL - Critical for journalist verification */}
      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-xs rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50 max-w-xs">
        <div className="font-bold mb-1">{type.charAt(0).toUpperCase() + type.slice(1)} Source</div>
        <div className="break-all font-mono text-[10px] mb-1">{url}</div>
        <div className="text-[9px] opacity-75 italic">Click to verify source</div>
        <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1 border-4 border-transparent border-t-gray-900 dark:border-t-gray-100"></div>
      </div>
    </div>
  )
}
