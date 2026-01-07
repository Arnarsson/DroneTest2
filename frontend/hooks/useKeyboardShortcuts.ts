import { useEffect, useCallback } from 'react'

/**
 * Map of keyboard keys to their callback functions.
 * Keys should be single characters (e.g., 'a', 'A', 'Escape').
 * Matching is case-insensitive for single letter keys.
 */
export type KeyboardShortcutMap = Record<string, () => void>

/**
 * Checks if the currently focused element is an input field
 * where keyboard shortcuts should be suppressed.
 */
function isInputElement(element: Element | null): boolean {
  if (!element) return false

  const tagName = element.tagName.toLowerCase()

  // Check for input, textarea, or select elements
  if (tagName === 'input' || tagName === 'textarea' || tagName === 'select') {
    return true
  }

  // Check for contenteditable elements
  if (element.getAttribute('contenteditable') === 'true') {
    return true
  }

  return false
}

/**
 * Custom hook for handling keyboard shortcuts.
 *
 * @param shortcuts - Map of key names to callback functions
 *
 * Features:
 * - Registers keydown event listener on mount
 * - Cleans up listener on unmount
 * - Ignores shortcuts when focus is on input, textarea, select, or contenteditable elements
 * - Supports case-insensitive key matching for single letter keys
 *
 * @example
 * ```tsx
 * useKeyboardShortcuts({
 *   'a': () => toggleAirports(),
 *   'm': () => toggleMilitary(),
 *   'Escape': () => closePanel(),
 * })
 * ```
 */
export function useKeyboardShortcuts(shortcuts: KeyboardShortcutMap): void {
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    // Ignore shortcuts when user is typing in form fields
    if (isInputElement(document.activeElement)) {
      return
    }

    // Get the pressed key
    const key = event.key

    // Try to find a matching shortcut (case-insensitive for single letters)
    let callback = shortcuts[key]

    if (!callback) {
      // Try case-insensitive match for single letter keys
      const lowerKey = key.toLowerCase()
      const upperKey = key.toUpperCase()

      callback = shortcuts[lowerKey] || shortcuts[upperKey]
    }

    // Execute the callback if found
    if (callback) {
      callback()
    }
  }, [shortcuts])

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])
}
