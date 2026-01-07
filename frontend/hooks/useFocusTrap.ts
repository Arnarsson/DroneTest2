'use client'

import { useEffect, useRef, useCallback, RefObject } from 'react'

/**
 * Selector for all focusable elements within a container.
 * Excludes elements with tabindex="-1" as they are programmatically
 * focusable but not part of the tab order.
 */
const FOCUSABLE_ELEMENTS_SELECTOR = [
  'button:not([disabled])',
  '[href]',
  'input:not([disabled])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
].join(', ')

interface UseFocusTrapOptions {
  /**
   * Whether the focus trap is currently active
   */
  isActive: boolean
  /**
   * Optional ref to the element that should receive initial focus.
   * If not provided, the first focusable element will receive focus.
   */
  initialFocusRef?: RefObject<HTMLElement | null>
  /**
   * Whether to return focus to the previously focused element when deactivated.
   * Defaults to true.
   */
  returnFocus?: boolean
}

/**
 * Custom hook to trap focus within a container element.
 *
 * This hook implements WCAG 2.1 and WAI-ARIA best practices for modal dialogs
 * by ensuring keyboard focus cycles only within the specified container when active.
 *
 * @param containerRef - Ref to the container element that should trap focus
 * @param options - Configuration options for the focus trap
 *
 * @example
 * ```tsx
 * const modalRef = useRef<HTMLDivElement>(null)
 * const closeButtonRef = useRef<HTMLButtonElement>(null)
 *
 * useFocusTrap(modalRef, {
 *   isActive: isModalOpen,
 *   initialFocusRef: closeButtonRef,
 *   returnFocus: true,
 * })
 * ```
 */
export function useFocusTrap(
  containerRef: RefObject<HTMLElement | null>,
  options: UseFocusTrapOptions
) {
  const { isActive, initialFocusRef, returnFocus = true } = options

  // Store the element that was focused before the trap was activated
  const previouslyFocusedRef = useRef<HTMLElement | null>(null)

  /**
   * Get all focusable elements within the container
   */
  const getFocusableElements = useCallback((): HTMLElement[] => {
    if (!containerRef.current) return []

    const elements = containerRef.current.querySelectorAll<HTMLElement>(
      FOCUSABLE_ELEMENTS_SELECTOR
    )

    // Filter out elements that are not visible
    return Array.from(elements).filter((element) => {
      return (
        element.offsetParent !== null &&
        !element.hasAttribute('hidden') &&
        getComputedStyle(element).visibility !== 'hidden'
      )
    })
  }, [containerRef])

  /**
   * Handle Tab/Shift+Tab key presses to trap focus within the container
   */
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (event.key !== 'Tab') return

      const focusableElements = getFocusableElements()
      if (focusableElements.length === 0) return

      const firstElement = focusableElements[0]
      const lastElement = focusableElements[focusableElements.length - 1]

      // Shift+Tab: if on first element, wrap to last
      if (event.shiftKey) {
        if (document.activeElement === firstElement) {
          event.preventDefault()
          lastElement.focus()
        }
      }
      // Tab: if on last element, wrap to first
      else {
        if (document.activeElement === lastElement) {
          event.preventDefault()
          firstElement.focus()
        }
      }
    },
    [getFocusableElements]
  )

  /**
   * Set initial focus when the trap is activated
   */
  useEffect(() => {
    if (!isActive) return

    // Store currently focused element for later restoration
    previouslyFocusedRef.current = document.activeElement as HTMLElement

    // Use requestAnimationFrame to ensure the container is rendered
    // and any animations have started
    const frameId = requestAnimationFrame(() => {
      if (initialFocusRef?.current) {
        initialFocusRef.current.focus()
      } else {
        const focusableElements = getFocusableElements()
        if (focusableElements.length > 0) {
          focusableElements[0].focus()
        }
      }
    })

    return () => {
      cancelAnimationFrame(frameId)
    }
  }, [isActive, initialFocusRef, getFocusableElements])

  /**
   * Restore focus when the trap is deactivated
   */
  useEffect(() => {
    if (isActive) return

    if (returnFocus && previouslyFocusedRef.current) {
      // Use requestAnimationFrame to ensure any exit animations complete
      const frameId = requestAnimationFrame(() => {
        previouslyFocusedRef.current?.focus()
        previouslyFocusedRef.current = null
      })
      return () => cancelAnimationFrame(frameId)
    }
  }, [isActive, returnFocus])

  /**
   * Add/remove keyboard event listener for focus trapping
   */
  useEffect(() => {
    if (!isActive) return

    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [isActive, handleKeyDown])
}
