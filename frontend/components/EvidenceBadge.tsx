'use client'

import { motion } from 'framer-motion'
import { EVIDENCE_SYSTEM, type EvidenceScore } from '@/constants/evidence'

interface EvidenceBadgeProps {
  score: EvidenceScore
  className?: string
  showTooltip?: boolean
  size?: 'sm' | 'md' | 'lg'
}

export function EvidenceBadge({ score, className = '', showTooltip = true, size = 'md' }: EvidenceBadgeProps) {
  const config = EVIDENCE_SYSTEM[score]

  const sizeClasses = {
    sm: 'text-[10px] px-2 py-1',
    md: 'text-xs px-4 py-2',
    lg: 'text-sm px-5 py-2.5'
  }

  const iconMap = {
    'shield': (
      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    ),
    'check-circle': (
      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    'alert-circle': (
      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    ),
    'help-circle': (
      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    )
  }

  const icon = iconMap[config.icon as keyof typeof iconMap]

  return (
    <div className="relative group inline-block">
      <div
        className={`${config.bgClass} ${config.textClass} ${sizeClasses[size]} rounded-full font-bold shadow-sm flex items-center gap-1.5 transition-all hover:shadow-md ${className}`}
        role="status"
        aria-label={`Evidence score: ${config.label}`}
      >
        {icon}
        <span>{config.label}</span>
      </div>

      {showTooltip && (
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-xs rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
          {config.description}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1 border-4 border-transparent border-t-gray-900 dark:border-t-gray-100"></div>
        </div>
      )}
    </div>
  )
}
