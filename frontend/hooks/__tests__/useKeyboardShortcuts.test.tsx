import React from 'react'
import { renderHook, act } from '@testing-library/react'
import { useKeyboardShortcuts } from '../useKeyboardShortcuts'

describe('useKeyboardShortcuts', () => {
  // Helper to dispatch keyboard events
  const dispatchKeydown = (key: string) => {
    const event = new KeyboardEvent('keydown', { key, bubbles: true })
    document.dispatchEvent(event)
  }

  // Helper to create a focused input element
  const createFocusedInput = (type: string = 'input'): HTMLElement => {
    const element = document.createElement(type)
    document.body.appendChild(element)
    element.focus()
    return element
  }

  beforeEach(() => {
    jest.clearAllMocks()
    // Reset focus to body
    if (document.activeElement instanceof HTMLElement) {
      document.activeElement.blur()
    }
  })

  afterEach(() => {
    // Clean up any elements added to the DOM
    document.body.innerHTML = ''
  })

  describe('callback invocation', () => {
    it('fires callback when correct key is pressed', () => {
      const callback = jest.fn()

      renderHook(() => useKeyboardShortcuts({ a: callback }))

      act(() => {
        dispatchKeydown('a')
      })

      expect(callback).toHaveBeenCalledTimes(1)
    })

    it('fires callback for multiple different keys', () => {
      const callbackA = jest.fn()
      const callbackM = jest.fn()
      const callbackT = jest.fn()

      renderHook(() =>
        useKeyboardShortcuts({
          a: callbackA,
          m: callbackM,
          t: callbackT,
        })
      )

      act(() => {
        dispatchKeydown('a')
        dispatchKeydown('m')
        dispatchKeydown('t')
      })

      expect(callbackA).toHaveBeenCalledTimes(1)
      expect(callbackM).toHaveBeenCalledTimes(1)
      expect(callbackT).toHaveBeenCalledTimes(1)
    })

    it('does not fire callback for unregistered keys', () => {
      const callback = jest.fn()

      renderHook(() => useKeyboardShortcuts({ a: callback }))

      act(() => {
        dispatchKeydown('b')
        dispatchKeydown('x')
        dispatchKeydown('z')
      })

      expect(callback).not.toHaveBeenCalled()
    })

    it('fires callback multiple times for repeated key presses', () => {
      const callback = jest.fn()

      renderHook(() => useKeyboardShortcuts({ a: callback }))

      act(() => {
        dispatchKeydown('a')
        dispatchKeydown('a')
        dispatchKeydown('a')
      })

      expect(callback).toHaveBeenCalledTimes(3)
    })
  })

  describe('case-insensitive key matching', () => {
    it('fires callback for lowercase key when uppercase is pressed', () => {
      const callback = jest.fn()

      renderHook(() => useKeyboardShortcuts({ a: callback }))

      act(() => {
        dispatchKeydown('A')
      })

      expect(callback).toHaveBeenCalledTimes(1)
    })

    it('fires callback for uppercase key when lowercase is pressed', () => {
      const callback = jest.fn()

      renderHook(() => useKeyboardShortcuts({ A: callback }))

      act(() => {
        dispatchKeydown('a')
      })

      expect(callback).toHaveBeenCalledTimes(1)
    })

    it('matches keys case-insensitively regardless of registration case', () => {
      const callbackLower = jest.fn()
      const callbackUpper = jest.fn()

      renderHook(() =>
        useKeyboardShortcuts({
          m: callbackLower,
          V: callbackUpper,
        })
      )

      act(() => {
        dispatchKeydown('M') // Uppercase when lowercase registered
        dispatchKeydown('v') // Lowercase when uppercase registered
      })

      expect(callbackLower).toHaveBeenCalledTimes(1)
      expect(callbackUpper).toHaveBeenCalledTimes(1)
    })
  })

  describe('input field detection', () => {
    it('ignores shortcuts when focus is on input element', () => {
      const callback = jest.fn()

      renderHook(() => useKeyboardShortcuts({ a: callback }))

      createFocusedInput('input')

      act(() => {
        dispatchKeydown('a')
      })

      expect(callback).not.toHaveBeenCalled()
    })

    it('ignores shortcuts when focus is on textarea element', () => {
      const callback = jest.fn()

      renderHook(() => useKeyboardShortcuts({ a: callback }))

      createFocusedInput('textarea')

      act(() => {
        dispatchKeydown('a')
      })

      expect(callback).not.toHaveBeenCalled()
    })

    it('ignores shortcuts when focus is on select element', () => {
      const callback = jest.fn()

      renderHook(() => useKeyboardShortcuts({ a: callback }))

      createFocusedInput('select')

      act(() => {
        dispatchKeydown('a')
      })

      expect(callback).not.toHaveBeenCalled()
    })

    it('ignores shortcuts when focus is on contenteditable element', () => {
      const callback = jest.fn()

      renderHook(() => useKeyboardShortcuts({ a: callback }))

      const element = document.createElement('div')
      element.setAttribute('contenteditable', 'true')
      document.body.appendChild(element)
      element.focus()

      act(() => {
        dispatchKeydown('a')
      })

      expect(callback).not.toHaveBeenCalled()
    })

    it('fires callback when focus returns to body from input', () => {
      const callback = jest.fn()

      renderHook(() => useKeyboardShortcuts({ a: callback }))

      const input = createFocusedInput('input')

      act(() => {
        dispatchKeydown('a')
      })

      expect(callback).not.toHaveBeenCalled()

      // Blur the input (focus goes back to body)
      input.blur()

      act(() => {
        dispatchKeydown('a')
      })

      expect(callback).toHaveBeenCalledTimes(1)
    })
  })

  describe('cleanup on unmount', () => {
    it('removes event listener when component unmounts', () => {
      const callback = jest.fn()

      const { unmount } = renderHook(() => useKeyboardShortcuts({ a: callback }))

      // Verify listener works before unmount
      act(() => {
        dispatchKeydown('a')
      })
      expect(callback).toHaveBeenCalledTimes(1)

      // Unmount the hook
      unmount()

      // Verify listener no longer fires after unmount
      act(() => {
        dispatchKeydown('a')
      })
      expect(callback).toHaveBeenCalledTimes(1) // Still 1, not 2
    })

    it('cleans up properly when shortcuts change', () => {
      const callback1 = jest.fn()
      const callback2 = jest.fn()

      const { rerender } = renderHook(
        ({ shortcuts }) => useKeyboardShortcuts(shortcuts),
        {
          initialProps: { shortcuts: { a: callback1 } },
        }
      )

      act(() => {
        dispatchKeydown('a')
      })
      expect(callback1).toHaveBeenCalledTimes(1)

      // Rerender with new shortcuts
      rerender({ shortcuts: { a: callback2 } })

      act(() => {
        dispatchKeydown('a')
      })

      // callback1 should not be called again
      expect(callback1).toHaveBeenCalledTimes(1)
      // callback2 should be called
      expect(callback2).toHaveBeenCalledTimes(1)
    })
  })

  describe('special keys', () => {
    it('handles Escape key', () => {
      const callback = jest.fn()

      renderHook(() => useKeyboardShortcuts({ Escape: callback }))

      act(() => {
        dispatchKeydown('Escape')
      })

      expect(callback).toHaveBeenCalledTimes(1)
    })

    it('handles Enter key', () => {
      const callback = jest.fn()

      renderHook(() => useKeyboardShortcuts({ Enter: callback }))

      act(() => {
        dispatchKeydown('Enter')
      })

      expect(callback).toHaveBeenCalledTimes(1)
    })
  })

  describe('empty shortcuts', () => {
    it('handles empty shortcuts map without errors', () => {
      expect(() => {
        renderHook(() => useKeyboardShortcuts({}))
      }).not.toThrow()
    })
  })
})
