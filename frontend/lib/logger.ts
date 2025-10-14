/**
 * Logger utility for DroneWatch
 *
 * Provides environment-aware logging:
 * - Development: All logs (log, debug, warn) go to console with [DroneWatch] prefix
 * - Production: Only errors are logged to console
 *
 * Usage:
 * import { logger } from '@/lib/logger'
 * logger.debug('API URL:', url)
 * logger.warn('Warning message')
 * logger.error('Error occurred', error)
 */

const isDev = process.env.NODE_ENV === 'development'

export const logger = {
  /**
   * General logging - only shown in development
   */
  log: (...args: any[]) => {
    if (isDev) console.log('[DroneWatch]', ...args)
  },

  /**
   * Debug logging - only shown in development
   * Use for detailed information during development
   */
  debug: (...args: any[]) => {
    if (isDev) console.debug('[DroneWatch]', ...args)
  },

  /**
   * Warning logging - only shown in development
   */
  warn: (...args: any[]) => {
    if (isDev) console.warn('[DroneWatch]', ...args)
  },

  /**
   * Error logging - ALWAYS logged (even in production)
   * Use for errors that need to be tracked
   */
  error: (...args: any[]) => {
    console.error('[DroneWatch]', ...args)
  },
}
