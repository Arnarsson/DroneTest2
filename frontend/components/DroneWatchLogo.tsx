'use client'

import { useTheme } from 'next-themes'

interface DroneWatchLogoProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function DroneWatchLogo({ size = 'md', className = '' }: DroneWatchLogoProps) {
  const { resolvedTheme } = useTheme()

  const sizeMap = {
    sm: { width: 24, height: 24 },
    md: { width: 32, height: 32 },
    lg: { width: 48, height: 48 }
  }

  const dimensions = sizeMap[size]

  // High contrast colors for better visibility
  const colors = {
    light: '#1E3A5F', // Dark navy for light mode
    dark: '#00D9FF'   // Bright cyan for dark mode
  }

  const fillColor = resolvedTheme === 'dark' ? colors.dark : colors.light

  return (
    <svg
      width={dimensions.width}
      height={dimensions.height}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`transition-colors duration-300 ${className}`}
      aria-label="DroneWatch logo"
      role="img"
    >
      {/* Simple, modern drone icon - minimalist design */}
      {/* Crosshair/target center (represents "watch") */}
      <circle
        cx="12"
        cy="12"
        r="2"
        fill={fillColor}
      />
      <circle
        cx="12"
        cy="12"
        r="5"
        stroke={fillColor}
        strokeWidth="1.5"
        fill="none"
      />

      {/* Four propellers (drone arms) */}
      {/* Top-left */}
      <circle cx="6" cy="6" r="2.5" fill={fillColor} opacity="0.8" />
      <line x1="8.5" y1="8.5" x2="9.5" y2="9.5" stroke={fillColor} strokeWidth="1.5" strokeLinecap="round" />

      {/* Top-right */}
      <circle cx="18" cy="6" r="2.5" fill={fillColor} opacity="0.8" />
      <line x1="15.5" y1="8.5" x2="14.5" y2="9.5" stroke={fillColor} strokeWidth="1.5" strokeLinecap="round" />

      {/* Bottom-left */}
      <circle cx="6" cy="18" r="2.5" fill={fillColor} opacity="0.8" />
      <line x1="8.5" y1="15.5" x2="9.5" y2="14.5" stroke={fillColor} strokeWidth="1.5" strokeLinecap="round" />

      {/* Bottom-right */}
      <circle cx="18" cy="18" r="2.5" fill={fillColor} opacity="0.8" />
      <line x1="15.5" y1="15.5" x2="14.5" y2="14.5" stroke={fillColor} strokeWidth="1.5" strokeLinecap="round" />

      {/* Subtle scan line effect */}
      <path
        d="M 7 12 L 17 12"
        stroke={fillColor}
        strokeWidth="0.5"
        opacity="0.4"
        strokeDasharray="2 2"
      />
    </svg>
  )
}
