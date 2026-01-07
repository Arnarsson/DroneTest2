import { renderHook, act } from '@testing-library/react'
import { useKeyboardShortcuts, SHORTCUT_KEYS, ShortcutMap } from '../useKeyboardShortcuts'

describe('useKeyboardShortcuts', () => {
  // Helper function to simulate a keyboard event
  const fireKeyboardEvent = (key: string, options: Partial<KeyboardEventInit> = {}) => {
    const event = new KeyboardEvent('keydown', {
      key,
      bubbles: true,
      cancelable: true,
      ...options,
    })
    act(() => {
      document.dispatchEvent(event)
    })
    return event
  }

  // Helper to set the active element (simulating focus)
  const setActiveElement = (element: HTMLElement | null) => {
    Object.defineProperty(document, 'activeElement', {
      value: element,
      writable: true,
      configurable: true,
    })
  }

  afterEach(() => {
    // Reset activeElement to body after each test
    setActiveElement(document.body)
  })

  describe('callback registration', () => {
    it('should call the handler when the registered key is pressed', () => {
      const handler = jest.fn()
      const shortcuts: ShortcutMap = { '1': handler }

      renderHook(() => useKeyboardShortcuts(shortcuts))

      fireKeyboardEvent('1')

      expect(handler).toHaveBeenCalledTimes(1)
    })

    it('should support multiple shortcuts', () => {
      const handler1 = jest.fn()
      const handler2 = jest.fn()
      const handler3 = jest.fn()
      const shortcuts: ShortcutMap = {
        '1': handler1,
        '2': handler2,
        '3': handler3,
      }

      renderHook(() => useKeyboardShortcuts(shortcuts))

      fireKeyboardEvent('1')
      fireKeyboardEvent('2')
      fireKeyboardEvent('3')

      expect(handler1).toHaveBeenCalledTimes(1)
      expect(handler2).toHaveBeenCalledTimes(1)
      expect(handler3).toHaveBeenCalledTimes(1)
    })

    it('should not call handler for unregistered keys', () => {
      const handler = jest.fn()
      const shortcuts: ShortcutMap = { '1': handler }

      renderHook(() => useKeyboardShortcuts(shortcuts))

      fireKeyboardEvent('2')
      fireKeyboardEvent('a')
      fireKeyboardEvent('Enter')

      expect(handler).not.toHaveBeenCalled()
    })

    it('should call handler multiple times when same key is pressed multiple times', () => {
      const handler = jest.fn()
      const shortcuts: ShortcutMap = { 'f': handler }

      renderHook(() => useKeyboardShortcuts(shortcuts))

      fireKeyboardEvent('f')
      fireKeyboardEvent('f')
      fireKeyboardEvent('f')

      expect(handler).toHaveBeenCalledTimes(3)
    })
  })

  describe('case-insensitive key handling', () => {
    it('should handle lowercase key press for lowercase-registered shortcut', () => {
      const handler = jest.fn()
      const shortcuts: ShortcutMap = { 'f': handler }

      renderHook(() => useKeyboardShortcuts(shortcuts))

      fireKeyboardEvent('f')

      expect(handler).toHaveBeenCalledTimes(1)
    })

    it('should handle uppercase key press for lowercase-registered shortcut', () => {
      const handler = jest.fn()
      const shortcuts: ShortcutMap = { 'f': handler }

      renderHook(() => useKeyboardShortcuts(shortcuts))

      fireKeyboardEvent('F')

      expect(handler).toHaveBeenCalledTimes(1)
    })

    it('should handle uppercase key press for uppercase-registered shortcut', () => {
      const handler = jest.fn()
      const shortcuts: ShortcutMap = { 'F': handler }

      renderHook(() => useKeyboardShortcuts(shortcuts))

      fireKeyboardEvent('F')

      expect(handler).toHaveBeenCalledTimes(1)
    })

    it('should handle lowercase key press for uppercase-registered shortcut', () => {
      const handler = jest.fn()
      const shortcuts: ShortcutMap = { 'F': handler }

      renderHook(() => useKeyboardShortcuts(shortcuts))

      fireKeyboardEvent('f')

      expect(handler).toHaveBeenCalledTimes(1)
    })
  })

  describe('input field detection', () => {
    it('should not fire shortcuts when focus is on an INPUT element', () => {
      const handler = jest.fn()
      const shortcuts: ShortcutMap = { '1': handler }

      renderHook(() => useKeyboardShortcuts(shortcuts))

      const input = document.createElement('input')
      document.body.appendChild(input)
      setActiveElement(input)

      fireKeyboardEvent('1')

      expect(handler).not.toHaveBeenCalled()
      document.body.removeChild(input)
    })

    it('should not fire shortcuts when focus is on a TEXTAREA element', () => {
      const handler = jest.fn()
      const shortcuts: ShortcutMap = { 'f': handler }

      renderHook(() => useKeyboardShortcuts(shortcuts))

      const textarea = document.createElement('textarea')
      document.body.appendChild(textarea)
      setActiveElement(textarea)

      fireKeyboardEvent('f')

      expect(handler).not.toHaveBeenCalled()
      document.body.removeChild(textarea)
    })

    it('should not fire shortcuts when focus is on a SELECT element', () => {
      const handler = jest.fn()
      const shortcuts: ShortcutMap = { '2': handler }

      renderHook(() => useKeyboardShortcuts(shortcuts))

      const select = document.createElement('select')
      document.body.appendChild(select)
      setActiveElement(select)

      fireKeyboardEvent('2')

      expect(handler).not.toHaveBeenCalled()
      document.body.removeChild(select)
    })

    it('should not fire shortcuts when focus is on a contenteditable element', () => {
      const handler = jest.fn()
      const shortcuts: ShortcutMap = { '3': handler }

      renderHook(() => useKeyboardShortcuts(shortcuts))

      const div = document.createElement('div')
      div.setAttribute('contenteditable', 'true')
      document.body.appendChild(div)
      setActiveElement(div)

      fireKeyboardEvent('3')

      expect(handler).not.toHaveBeenCalled()
      document.body.removeChild(div)
    })

    it('should fire shortcuts when focus is on a regular DIV element', () => {
      const handler = jest.fn()
      const shortcuts: ShortcutMap = { '1': handler }

      renderHook(() => useKeyboardShortcuts(shortcuts))

      const div = document.createElement('div')
      document.body.appendChild(div)
      setActiveElement(div)

      fireKeyboardEvent('1')

      expect(handler).toHaveBeenCalledTimes(1)
      document.body.removeChild(div)
    })

    it('should fire shortcuts when focus is on a BUTTON element', () => {
      const handler = jest.fn()
      const shortcuts: ShortcutMap = { 'f': handler }

      renderHook(() => useKeyboardShortcuts(shortcuts))

      const button = document.createElement('button')
      document.body.appendChild(button)
      setActiveElement(button)

      fireKeyboardEvent('f')

      expect(handler).toHaveBeenCalledTimes(1)
      document.body.removeChild(button)
    })
  })

  describe('modifier keys', () => {
    it('should not fire shortcuts when Ctrl key is held', () => {
      const handler = jest.fn()
      const shortcuts: ShortcutMap = { '1': handler }

      renderHook(() => useKeyboardShortcuts(shortcuts))

      fireKeyboardEvent('1', { ctrlKey: true })

      expect(handler).not.toHaveBeenCalled()
    })

    it('should not fire shortcuts when Meta key is held', () => {
      const handler = jest.fn()
      const shortcuts: ShortcutMap = { '1': handler }

      renderHook(() => useKeyboardShortcuts(shortcuts))

      fireKeyboardEvent('1', { metaKey: true })

      expect(handler).not.toHaveBeenCalled()
    })

    it('should not fire shortcuts when Alt key is held', () => {
      const handler = jest.fn()
      const shortcuts: ShortcutMap = { '1': handler }

      renderHook(() => useKeyboardShortcuts(shortcuts))

      fireKeyboardEvent('1', { altKey: true })

      expect(handler).not.toHaveBeenCalled()
    })

    it('should fire shortcuts when Shift key is held (for uppercase)', () => {
      const handler = jest.fn()
      const shortcuts: ShortcutMap = { 'f': handler }

      renderHook(() => useKeyboardShortcuts(shortcuts))

      // Shift + f = 'F'
      fireKeyboardEvent('F', { shiftKey: true })

      expect(handler).toHaveBeenCalledTimes(1)
    })
  })

  describe('cleanup on unmount', () => {
    it('should remove event listeners when component unmounts', () => {
      const handler = jest.fn()
      const shortcuts: ShortcutMap = { '1': handler }

      const { unmount } = renderHook(() => useKeyboardShortcuts(shortcuts))

      // Verify handler works before unmount
      fireKeyboardEvent('1')
      expect(handler).toHaveBeenCalledTimes(1)

      // Unmount the hook
      unmount()

      // Handler should not be called after unmount
      fireKeyboardEvent('1')
      expect(handler).toHaveBeenCalledTimes(1) // Still 1, not 2
    })

    it('should not leak event listeners across multiple hook instances', () => {
      const handler1 = jest.fn()
      const handler2 = jest.fn()

      const { unmount: unmount1 } = renderHook(() =>
        useKeyboardShortcuts({ '1': handler1 })
      )
      const { unmount: unmount2 } = renderHook(() =>
        useKeyboardShortcuts({ '2': handler2 })
      )

      fireKeyboardEvent('1')
      fireKeyboardEvent('2')
      expect(handler1).toHaveBeenCalledTimes(1)
      expect(handler2).toHaveBeenCalledTimes(1)

      // Unmount first hook
      unmount1()

      fireKeyboardEvent('1')
      fireKeyboardEvent('2')
      expect(handler1).toHaveBeenCalledTimes(1) // Not called again
      expect(handler2).toHaveBeenCalledTimes(2) // Still working

      // Unmount second hook
      unmount2()

      fireKeyboardEvent('1')
      fireKeyboardEvent('2')
      expect(handler1).toHaveBeenCalledTimes(1)
      expect(handler2).toHaveBeenCalledTimes(2) // Not called again
    })
  })

  describe('enabled parameter', () => {
    it('should not register listeners when enabled is false', () => {
      const handler = jest.fn()
      const shortcuts: ShortcutMap = { '1': handler }

      renderHook(() => useKeyboardShortcuts(shortcuts, false))

      fireKeyboardEvent('1')

      expect(handler).not.toHaveBeenCalled()
    })

    it('should register listeners when enabled is true (default)', () => {
      const handler = jest.fn()
      const shortcuts: ShortcutMap = { '1': handler }

      renderHook(() => useKeyboardShortcuts(shortcuts, true))

      fireKeyboardEvent('1')

      expect(handler).toHaveBeenCalledTimes(1)
    })

    it('should toggle listeners when enabled changes', () => {
      const handler = jest.fn()
      const shortcuts: ShortcutMap = { '1': handler }

      const { rerender } = renderHook(
        ({ enabled }) => useKeyboardShortcuts(shortcuts, enabled),
        { initialProps: { enabled: true } }
      )

      fireKeyboardEvent('1')
      expect(handler).toHaveBeenCalledTimes(1)

      // Disable shortcuts
      rerender({ enabled: false })

      fireKeyboardEvent('1')
      expect(handler).toHaveBeenCalledTimes(1) // Still 1

      // Re-enable shortcuts
      rerender({ enabled: true })

      fireKeyboardEvent('1')
      expect(handler).toHaveBeenCalledTimes(2)
    })
  })

  describe('SHORTCUT_KEYS constants', () => {
    it('should have MAP_VIEW set to "1"', () => {
      expect(SHORTCUT_KEYS.MAP_VIEW).toBe('1')
    })

    it('should have LIST_VIEW set to "2"', () => {
      expect(SHORTCUT_KEYS.LIST_VIEW).toBe('2')
    })

    it('should have ANALYTICS_VIEW set to "3"', () => {
      expect(SHORTCUT_KEYS.ANALYTICS_VIEW).toBe('3')
    })

    it('should have FILTER_TOGGLE set to "f"', () => {
      expect(SHORTCUT_KEYS.FILTER_TOGGLE).toBe('f')
    })
  })

  describe('event.preventDefault', () => {
    it('should call preventDefault when a shortcut is triggered', () => {
      const handler = jest.fn()
      const shortcuts: ShortcutMap = { '1': handler }
      const preventDefaultSpy = jest.fn()

      renderHook(() => useKeyboardShortcuts(shortcuts))

      // Create a custom event with a spy on preventDefault
      const event = new KeyboardEvent('keydown', {
        key: '1',
        bubbles: true,
        cancelable: true,
      })
      Object.defineProperty(event, 'preventDefault', {
        value: preventDefaultSpy,
        writable: true,
      })

      act(() => {
        document.dispatchEvent(event)
      })

      expect(preventDefaultSpy).toHaveBeenCalled()
    })

    it('should not call preventDefault when key is not registered', () => {
      const handler = jest.fn()
      const shortcuts: ShortcutMap = { '1': handler }
      const preventDefaultSpy = jest.fn()

      renderHook(() => useKeyboardShortcuts(shortcuts))

      const event = new KeyboardEvent('keydown', {
        key: '9',
        bubbles: true,
        cancelable: true,
      })
      Object.defineProperty(event, 'preventDefault', {
        value: preventDefaultSpy,
        writable: true,
      })

      act(() => {
        document.dispatchEvent(event)
      })

      expect(preventDefaultSpy).not.toHaveBeenCalled()
    })
  })

  describe('shortcuts update', () => {
    it('should respond to updated shortcuts when rerendered', () => {
      const handler1 = jest.fn()
      const handler2 = jest.fn()

      const { rerender } = renderHook(
        ({ shortcuts }) => useKeyboardShortcuts(shortcuts),
        { initialProps: { shortcuts: { '1': handler1 } as ShortcutMap } }
      )

      fireKeyboardEvent('1')
      expect(handler1).toHaveBeenCalledTimes(1)
      expect(handler2).not.toHaveBeenCalled()

      // Update shortcuts
      rerender({ shortcuts: { '1': handler2 } })

      fireKeyboardEvent('1')
      expect(handler1).toHaveBeenCalledTimes(1) // Not called again
      expect(handler2).toHaveBeenCalledTimes(1)
    })
  })
})
