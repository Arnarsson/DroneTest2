import { useEffect, useCallback } from 'react'

/**
 * Type for a keyboard shortcut handler callback
 */
export type ShortcutHandler = () => void

/**
 * Configuration for a single keyboard shortcut
 */
export interface KeyboardShortcut {
  /** The key to listen for (case-insensitive) */
  key: string
  /** The callback to execute when the key is pressed */
  handler: ShortcutHandler
  /** Optional description for accessibility/help purposes */
  description?: string
}

/**
 * Map of shortcut keys to their handlers
 */
export type ShortcutMap = Record<string, ShortcutHandler>

/**
 * Shortcut key constants for view switching and filter panel
 */
export const SHORTCUT_KEYS = {
  MAP_VIEW: '1',
  LIST_VIEW: '2',
  ANALYTICS_VIEW: '3',
  FILTER_TOGGLE: 'f',
} as const

/**
 * Elements that should not trigger shortcuts when focused
 */
const IGNORED_ELEMENTS = ['INPUT', 'TEXTAREA', 'SELECT']

/**
 * Check if the currently focused element should prevent shortcuts from firing
 */
function isInputFocused(): boolean {
  const activeElement = document.activeElement
  if (!activeElement) return false

  // Check if it's a form input element
  if (IGNORED_ELEMENTS.includes(activeElement.tagName)) {
    return true
  }

  // Check if it's a contenteditable element
  if (activeElement.getAttribute('contenteditable') === 'true') {
    return true
  }

  return false
}

/**
 * Custom hook for registering global keyboard shortcuts
 *
 * @param shortcuts - Map of key strings to handler functions
 * @param enabled - Whether shortcuts should be active (default: true)
 *
 * @example
 * ```tsx
 * useKeyboardShortcuts({
 *   '1': () => setView('map'),
 *   '2': () => setView('list'),
 *   '3': () => setView('analytics'),
 *   'f': () => setIsFilterPanelOpen(prev => !prev),
 * })
 * ```
 */
export function useKeyboardShortcuts(
  shortcuts: ShortcutMap,
  enabled: boolean = true
): void {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      // Don't fire shortcuts when typing in input fields
      if (isInputFocused()) {
        return
      }

      // Don't fire shortcuts when modifier keys are held (allow browser shortcuts)
      if (event.ctrlKey || event.metaKey || event.altKey) {
        return
      }

      // Normalize the key to lowercase for case-insensitive matching
      const key = event.key.toLowerCase()

      // Check if we have a handler for this key
      const handler = shortcuts[key] || shortcuts[key.toUpperCase()]

      if (handler) {
        event.preventDefault()
        handler()
      }
    },
    [shortcuts]
  )

  useEffect(() => {
    if (!enabled) {
      return
    }

    document.addEventListener('keydown', handleKeyDown)

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [handleKeyDown, enabled])
}
