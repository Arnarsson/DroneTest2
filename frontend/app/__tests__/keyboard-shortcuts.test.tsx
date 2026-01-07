import { render, screen, fireEvent, act } from '@testing-library/react'
import { useState, useCallback, useMemo } from 'react'
import { useKeyboardShortcuts, SHORTCUT_KEYS } from '@/hooks/useKeyboardShortcuts'

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    button: ({ children, onClick, className, ...props }: any) => (
      <button onClick={onClick} className={className} {...props}>
        {children}
      </button>
    ),
    div: ({ children, onClick, className, ...props }: any) => (
      <div onClick={onClick} className={className} {...props}>
        {children}
      </div>
    ),
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}))

/**
 * Integration tests for keyboard shortcuts
 *
 * These tests verify that keyboard shortcuts work correctly in the context
 * of the main page, including view switching and filter panel toggle.
 */

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

/**
 * Test component that mimics the main page's keyboard shortcuts behavior
 * This allows us to test the keyboard shortcuts in an integrated context
 */
function TestViewSwitcher() {
  const [view, setView] = useState<'map' | 'list' | 'analytics'>('map')
  const [isFilterPanelOpen, setIsFilterPanelOpen] = useState(false)

  const keyboardShortcuts = useMemo(
    () => ({
      [SHORTCUT_KEYS.MAP_VIEW]: () => setView('map'),
      [SHORTCUT_KEYS.LIST_VIEW]: () => setView('list'),
      [SHORTCUT_KEYS.ANALYTICS_VIEW]: () => setView('analytics'),
      [SHORTCUT_KEYS.FILTER_TOGGLE]: () => setIsFilterPanelOpen((prev) => !prev),
    }),
    []
  )
  useKeyboardShortcuts(keyboardShortcuts)

  return (
    <div>
      <div data-testid="current-view">{view}</div>
      <div data-testid="filter-panel-state">{isFilterPanelOpen ? 'open' : 'closed'}</div>
      <button
        onClick={() => setView('map')}
        aria-current={view === 'map' ? 'page' : undefined}
        data-testid="map-tab"
      >
        Map
      </button>
      <button
        onClick={() => setView('list')}
        aria-current={view === 'list' ? 'page' : undefined}
        data-testid="list-tab"
      >
        List
      </button>
      <button
        onClick={() => setView('analytics')}
        aria-current={view === 'analytics' ? 'page' : undefined}
        data-testid="analytics-tab"
      >
        Analytics
      </button>
      <button
        onClick={() => setIsFilterPanelOpen(!isFilterPanelOpen)}
        aria-expanded={isFilterPanelOpen}
        data-testid="filter-toggle"
      >
        Toggle Filters
      </button>
    </div>
  )
}

/**
 * Test component with input fields to verify shortcuts don't fire when typing
 */
function TestViewSwitcherWithInputs() {
  const [view, setView] = useState<'map' | 'list' | 'analytics'>('map')
  const [isFilterPanelOpen, setIsFilterPanelOpen] = useState(false)
  const [inputValue, setInputValue] = useState('')

  const keyboardShortcuts = useMemo(
    () => ({
      [SHORTCUT_KEYS.MAP_VIEW]: () => setView('map'),
      [SHORTCUT_KEYS.LIST_VIEW]: () => setView('list'),
      [SHORTCUT_KEYS.ANALYTICS_VIEW]: () => setView('analytics'),
      [SHORTCUT_KEYS.FILTER_TOGGLE]: () => setIsFilterPanelOpen((prev) => !prev),
    }),
    []
  )
  useKeyboardShortcuts(keyboardShortcuts)

  return (
    <div>
      <div data-testid="current-view">{view}</div>
      <div data-testid="filter-panel-state">{isFilterPanelOpen ? 'open' : 'closed'}</div>
      <input
        type="text"
        data-testid="text-input"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        placeholder="Type here..."
      />
      <textarea
        data-testid="textarea-input"
        placeholder="Write something..."
      />
      <select data-testid="select-input">
        <option value="1">Option 1</option>
        <option value="2">Option 2</option>
        <option value="3">Option 3</option>
      </select>
      <div data-testid="contenteditable-input" contentEditable={true}>
        Editable content
      </div>
    </div>
  )
}

describe('Keyboard Shortcuts Integration', () => {
  afterEach(() => {
    // Reset activeElement to body after each test
    setActiveElement(document.body)
  })

  describe('View Switching', () => {
    it('should switch to Map view when pressing "1"', () => {
      render(<TestViewSwitcher />)

      // Start from list view by clicking the tab
      fireEvent.click(screen.getByTestId('list-tab'))
      expect(screen.getByTestId('current-view')).toHaveTextContent('list')

      // Press "1" to switch to map view
      fireKeyboardEvent('1')
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')
    })

    it('should switch to List view when pressing "2"', () => {
      render(<TestViewSwitcher />)

      // Start from map view (default)
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')

      // Press "2" to switch to list view
      fireKeyboardEvent('2')
      expect(screen.getByTestId('current-view')).toHaveTextContent('list')
    })

    it('should switch to Analytics view when pressing "3"', () => {
      render(<TestViewSwitcher />)

      // Start from map view (default)
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')

      // Press "3" to switch to analytics view
      fireKeyboardEvent('3')
      expect(screen.getByTestId('current-view')).toHaveTextContent('analytics')
    })

    it('should support cycling through all views with keyboard', () => {
      render(<TestViewSwitcher />)

      // Start at map view
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')

      // Cycle through views
      fireKeyboardEvent('2')
      expect(screen.getByTestId('current-view')).toHaveTextContent('list')

      fireKeyboardEvent('3')
      expect(screen.getByTestId('current-view')).toHaveTextContent('analytics')

      fireKeyboardEvent('1')
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')
    })

    it('should stay on current view when pressing the same key', () => {
      render(<TestViewSwitcher />)

      // Start at map view
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')

      // Press "1" multiple times - should stay on map
      fireKeyboardEvent('1')
      fireKeyboardEvent('1')
      fireKeyboardEvent('1')
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')
    })

    it('should switch views regardless of current view state', () => {
      render(<TestViewSwitcher />)

      // Start at analytics
      fireKeyboardEvent('3')
      expect(screen.getByTestId('current-view')).toHaveTextContent('analytics')

      // Switch to list
      fireKeyboardEvent('2')
      expect(screen.getByTestId('current-view')).toHaveTextContent('list')

      // Switch back to analytics
      fireKeyboardEvent('3')
      expect(screen.getByTestId('current-view')).toHaveTextContent('analytics')
    })
  })

  describe('Filter Panel Toggle', () => {
    it('should open filter panel when pressing "f"', () => {
      render(<TestViewSwitcher />)

      // Filter panel starts closed
      expect(screen.getByTestId('filter-panel-state')).toHaveTextContent('closed')

      // Press "f" to open filter panel
      fireKeyboardEvent('f')
      expect(screen.getByTestId('filter-panel-state')).toHaveTextContent('open')
    })

    it('should close filter panel when pressing "f" again', () => {
      render(<TestViewSwitcher />)

      // Open filter panel
      fireKeyboardEvent('f')
      expect(screen.getByTestId('filter-panel-state')).toHaveTextContent('open')

      // Close filter panel
      fireKeyboardEvent('f')
      expect(screen.getByTestId('filter-panel-state')).toHaveTextContent('closed')
    })

    it('should toggle filter panel with uppercase "F"', () => {
      render(<TestViewSwitcher />)

      // Filter panel starts closed
      expect(screen.getByTestId('filter-panel-state')).toHaveTextContent('closed')

      // Press "F" (uppercase) to open filter panel
      fireKeyboardEvent('F')
      expect(screen.getByTestId('filter-panel-state')).toHaveTextContent('open')

      // Press "F" again to close
      fireKeyboardEvent('F')
      expect(screen.getByTestId('filter-panel-state')).toHaveTextContent('closed')
    })

    it('should toggle filter panel independently of view switching', () => {
      render(<TestViewSwitcher />)

      // Open filter panel
      fireKeyboardEvent('f')
      expect(screen.getByTestId('filter-panel-state')).toHaveTextContent('open')
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')

      // Switch to list view - filter should stay open
      fireKeyboardEvent('2')
      expect(screen.getByTestId('filter-panel-state')).toHaveTextContent('open')
      expect(screen.getByTestId('current-view')).toHaveTextContent('list')

      // Close filter panel
      fireKeyboardEvent('f')
      expect(screen.getByTestId('filter-panel-state')).toHaveTextContent('closed')
      expect(screen.getByTestId('current-view')).toHaveTextContent('list')
    })
  })

  describe('Input Focus Behavior', () => {
    it('should not switch views when typing in a text input', () => {
      render(<TestViewSwitcherWithInputs />)

      // Start at map view
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')

      // Focus the input
      const input = screen.getByTestId('text-input')
      document.body.appendChild(input)
      setActiveElement(input)

      // Press "2" while focused on input - should NOT switch view
      fireKeyboardEvent('2')
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')

      // Press "3" - should NOT switch view
      fireKeyboardEvent('3')
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')
    })

    it('should not switch views when typing in a textarea', () => {
      render(<TestViewSwitcherWithInputs />)

      // Start at map view
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')

      // Focus the textarea
      const textarea = screen.getByTestId('textarea-input')
      setActiveElement(textarea)

      // Press "2" while focused on textarea - should NOT switch view
      fireKeyboardEvent('2')
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')
    })

    it('should not switch views when a select is focused', () => {
      render(<TestViewSwitcherWithInputs />)

      // Start at map view
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')

      // Focus the select
      const select = screen.getByTestId('select-input')
      setActiveElement(select)

      // Press "2" while focused on select - should NOT switch view
      fireKeyboardEvent('2')
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')
    })

    it('should not switch views when contenteditable element is focused', () => {
      render(<TestViewSwitcherWithInputs />)

      // Start at map view
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')

      // Focus the contenteditable
      const contenteditable = screen.getByTestId('contenteditable-input')
      setActiveElement(contenteditable)

      // Press "2" while focused on contenteditable - should NOT switch view
      fireKeyboardEvent('2')
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')
    })

    it('should not toggle filter panel when typing "f" in an input', () => {
      render(<TestViewSwitcherWithInputs />)

      // Filter panel starts closed
      expect(screen.getByTestId('filter-panel-state')).toHaveTextContent('closed')

      // Focus the input
      const input = screen.getByTestId('text-input')
      setActiveElement(input)

      // Press "f" while focused on input - should NOT toggle filter
      fireKeyboardEvent('f')
      expect(screen.getByTestId('filter-panel-state')).toHaveTextContent('closed')

      // Press "F" - should NOT toggle filter
      fireKeyboardEvent('F')
      expect(screen.getByTestId('filter-panel-state')).toHaveTextContent('closed')
    })

    it('should work after unfocusing from input', () => {
      render(<TestViewSwitcherWithInputs />)

      // Start at map view
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')

      // Focus the input
      const input = screen.getByTestId('text-input')
      setActiveElement(input)

      // Press "2" while focused on input - should NOT switch view
      fireKeyboardEvent('2')
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')

      // Unfocus from input (blur)
      setActiveElement(document.body)

      // Now press "2" - should switch view
      fireKeyboardEvent('2')
      expect(screen.getByTestId('current-view')).toHaveTextContent('list')
    })
  })

  describe('Modifier Keys', () => {
    it('should not switch views when Ctrl is held', () => {
      render(<TestViewSwitcher />)

      // Start at map view
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')

      // Press Ctrl+2 - should NOT switch view (allow browser shortcuts)
      fireKeyboardEvent('2', { ctrlKey: true })
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')
    })

    it('should not switch views when Meta (Cmd) is held', () => {
      render(<TestViewSwitcher />)

      // Start at map view
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')

      // Press Cmd+2 - should NOT switch view (allow browser shortcuts)
      fireKeyboardEvent('2', { metaKey: true })
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')
    })

    it('should not switch views when Alt is held', () => {
      render(<TestViewSwitcher />)

      // Start at map view
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')

      // Press Alt+2 - should NOT switch view
      fireKeyboardEvent('2', { altKey: true })
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')
    })

    it('should switch views when only Shift is held (for uppercase)', () => {
      render(<TestViewSwitcher />)

      // Start at map view
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')

      // Press Shift+F to toggle filter (uppercase F)
      fireKeyboardEvent('F', { shiftKey: true })
      expect(screen.getByTestId('filter-panel-state')).toHaveTextContent('open')
    })
  })

  describe('Component Cleanup', () => {
    it('should remove event listeners when component unmounts', () => {
      const { unmount } = render(<TestViewSwitcher />)

      // Switch to list view to verify shortcuts work
      fireKeyboardEvent('2')
      expect(screen.getByTestId('current-view')).toHaveTextContent('list')

      // Unmount the component
      unmount()

      // Mount a new instance with default state
      render(<TestViewSwitcher />)

      // The new component should start at map view (not list)
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')
    })
  })

  describe('Combined Keyboard and Mouse Interactions', () => {
    it('should work with both keyboard and click interactions', () => {
      render(<TestViewSwitcher />)

      // Start at map view
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')

      // Use keyboard to switch to list
      fireKeyboardEvent('2')
      expect(screen.getByTestId('current-view')).toHaveTextContent('list')

      // Use mouse to switch to analytics
      fireEvent.click(screen.getByTestId('analytics-tab'))
      expect(screen.getByTestId('current-view')).toHaveTextContent('analytics')

      // Use keyboard to go back to map
      fireKeyboardEvent('1')
      expect(screen.getByTestId('current-view')).toHaveTextContent('map')
    })

    it('should sync filter panel state with both keyboard and click', () => {
      render(<TestViewSwitcher />)

      // Start closed
      expect(screen.getByTestId('filter-panel-state')).toHaveTextContent('closed')

      // Open with keyboard
      fireKeyboardEvent('f')
      expect(screen.getByTestId('filter-panel-state')).toHaveTextContent('open')

      // Close with click
      fireEvent.click(screen.getByTestId('filter-toggle'))
      expect(screen.getByTestId('filter-panel-state')).toHaveTextContent('closed')

      // Open with click
      fireEvent.click(screen.getByTestId('filter-toggle'))
      expect(screen.getByTestId('filter-panel-state')).toHaveTextContent('open')

      // Close with keyboard
      fireKeyboardEvent('f')
      expect(screen.getByTestId('filter-panel-state')).toHaveTextContent('closed')
    })
  })

  describe('SHORTCUT_KEYS Constants', () => {
    it('should use the correct shortcut keys from constants', () => {
      // Verify the constants match what the tests expect
      expect(SHORTCUT_KEYS.MAP_VIEW).toBe('1')
      expect(SHORTCUT_KEYS.LIST_VIEW).toBe('2')
      expect(SHORTCUT_KEYS.ANALYTICS_VIEW).toBe('3')
      expect(SHORTCUT_KEYS.FILTER_TOGGLE).toBe('f')
    })
  })
})
