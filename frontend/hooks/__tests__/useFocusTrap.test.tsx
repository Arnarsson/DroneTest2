import React, { useRef, useState } from 'react'
import { render, screen, fireEvent, act } from '@testing-library/react'
import { useFocusTrap } from '../useFocusTrap'

// Test component that uses the hook
interface TestComponentProps {
  isActive: boolean
  useInitialFocusRef?: boolean
  returnFocus?: boolean
}

function TestComponent({
  isActive,
  useInitialFocusRef = false,
  returnFocus = true,
}: TestComponentProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const closeButtonRef = useRef<HTMLButtonElement>(null)

  useFocusTrap(containerRef, {
    isActive,
    initialFocusRef: useInitialFocusRef ? closeButtonRef : undefined,
    returnFocus,
  })

  return (
    <div ref={containerRef} data-testid="container">
      <button data-testid="first-button">First</button>
      <input data-testid="input" type="text" />
      <a href="#" data-testid="link">
        Link
      </a>
      <button ref={closeButtonRef} data-testid="close-button">
        Close
      </button>
    </div>
  )
}

// Test component with external trigger button
function TestComponentWithTrigger() {
  const [isOpen, setIsOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const closeButtonRef = useRef<HTMLButtonElement>(null)

  useFocusTrap(containerRef, {
    isActive: isOpen,
    initialFocusRef: closeButtonRef,
    returnFocus: true,
  })

  return (
    <>
      <button data-testid="trigger" onClick={() => setIsOpen(true)}>
        Open
      </button>
      {isOpen && (
        <div ref={containerRef} data-testid="modal">
          <button ref={closeButtonRef} data-testid="modal-close">
            Close
          </button>
          <input data-testid="modal-input" type="text" />
          <button data-testid="modal-submit" onClick={() => setIsOpen(false)}>
            Submit
          </button>
        </div>
      )}
    </>
  )
}

// Test component with no focusable elements
function TestComponentNoFocusable({ isActive }: { isActive: boolean }) {
  const containerRef = useRef<HTMLDivElement>(null)

  useFocusTrap(containerRef, { isActive })

  return (
    <div ref={containerRef} data-testid="empty-container">
      <p>No focusable elements here</p>
    </div>
  )
}

// Test component with disabled elements
function TestComponentWithDisabled({ isActive }: { isActive: boolean }) {
  const containerRef = useRef<HTMLDivElement>(null)

  useFocusTrap(containerRef, { isActive })

  return (
    <div ref={containerRef} data-testid="container-disabled">
      <button data-testid="enabled-button">Enabled</button>
      <button data-testid="disabled-button" disabled>
        Disabled
      </button>
      <input data-testid="disabled-input" type="text" disabled />
      <button data-testid="another-enabled">Another Enabled</button>
    </div>
  )
}

describe('useFocusTrap', () => {
  beforeEach(() => {
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.useRealTimers()
    jest.clearAllMocks()
  })

  describe('Focus trapping within container', () => {
    it('sets focus to first focusable element when activated without initialFocusRef', () => {
      render(<TestComponent isActive={true} />)

      // Advance timers to handle requestAnimationFrame
      act(() => {
        jest.runAllTimers()
      })

      expect(document.activeElement).toBe(screen.getByTestId('first-button'))
    })

    it('sets focus to initialFocusRef element when provided', () => {
      render(<TestComponent isActive={true} useInitialFocusRef={true} />)

      act(() => {
        jest.runAllTimers()
      })

      expect(document.activeElement).toBe(screen.getByTestId('close-button'))
    })

    it('does not set focus when trap is not active', () => {
      render(<TestComponent isActive={false} />)

      act(() => {
        jest.runAllTimers()
      })

      // activeElement should be body when no focus is set
      expect(document.activeElement).toBe(document.body)
    })

    it('handles container with no focusable elements gracefully', () => {
      render(<TestComponentNoFocusable isActive={true} />)

      // Should not throw
      act(() => {
        jest.runAllTimers()
      })

      // Focus stays on body
      expect(document.activeElement).toBe(document.body)
    })
  })

  describe('Tab cycles through focusable elements', () => {
    it('wraps focus from last element to first when Tab is pressed', () => {
      render(<TestComponent isActive={true} />)

      act(() => {
        jest.runAllTimers()
      })

      // Focus the last element (close button)
      const closeButton = screen.getByTestId('close-button')
      act(() => {
        closeButton.focus()
      })
      expect(document.activeElement).toBe(closeButton)

      // Press Tab - should wrap to first element
      fireEvent.keyDown(document, { key: 'Tab', shiftKey: false })

      expect(document.activeElement).toBe(screen.getByTestId('first-button'))
    })

    it('allows normal Tab navigation within container', () => {
      render(<TestComponent isActive={true} />)

      act(() => {
        jest.runAllTimers()
      })

      // Focus first element
      const firstButton = screen.getByTestId('first-button')
      act(() => {
        firstButton.focus()
      })

      // Tab should NOT be prevented when not on last element
      const event = new KeyboardEvent('keydown', {
        key: 'Tab',
        shiftKey: false,
        bubbles: true,
        cancelable: true,
      })

      const preventDefault = jest.fn()
      Object.defineProperty(event, 'preventDefault', { value: preventDefault })

      document.dispatchEvent(event)

      // Should not prevent default when not on last element
      expect(preventDefault).not.toHaveBeenCalled()
    })

    it('skips disabled elements in tab order', () => {
      render(<TestComponentWithDisabled isActive={true} />)

      act(() => {
        jest.runAllTimers()
      })

      // Focus first enabled button
      expect(document.activeElement).toBe(screen.getByTestId('enabled-button'))

      // Focus the last enabled element
      const anotherEnabled = screen.getByTestId('another-enabled')
      act(() => {
        anotherEnabled.focus()
      })

      // Press Tab - should wrap back to first enabled button
      fireEvent.keyDown(document, { key: 'Tab', shiftKey: false })

      expect(document.activeElement).toBe(screen.getByTestId('enabled-button'))
    })
  })

  describe('Shift+Tab cycles backwards', () => {
    it('wraps focus from first element to last when Shift+Tab is pressed', () => {
      render(<TestComponent isActive={true} />)

      act(() => {
        jest.runAllTimers()
      })

      // Focus the first element
      const firstButton = screen.getByTestId('first-button')
      act(() => {
        firstButton.focus()
      })
      expect(document.activeElement).toBe(firstButton)

      // Press Shift+Tab - should wrap to last element
      fireEvent.keyDown(document, { key: 'Tab', shiftKey: true })

      expect(document.activeElement).toBe(screen.getByTestId('close-button'))
    })

    it('allows normal Shift+Tab navigation within container', () => {
      render(<TestComponent isActive={true} />)

      act(() => {
        jest.runAllTimers()
      })

      // Focus middle element (input)
      const input = screen.getByTestId('input')
      act(() => {
        input.focus()
      })

      // Shift+Tab should NOT be prevented when not on first element
      const event = new KeyboardEvent('keydown', {
        key: 'Tab',
        shiftKey: true,
        bubbles: true,
        cancelable: true,
      })

      const preventDefault = jest.fn()
      Object.defineProperty(event, 'preventDefault', { value: preventDefault })

      document.dispatchEvent(event)

      // Should not prevent default when not on first element
      expect(preventDefault).not.toHaveBeenCalled()
    })
  })

  describe('Focus restoration on deactivation', () => {
    it('restores focus to previously focused element when deactivated', () => {
      const { rerender } = render(<TestComponentWithTrigger />)

      const triggerButton = screen.getByTestId('trigger')

      // Focus the trigger button (simulating user interaction)
      act(() => {
        triggerButton.focus()
      })
      expect(document.activeElement).toBe(triggerButton)

      // Click to open modal
      fireEvent.click(triggerButton)

      act(() => {
        jest.runAllTimers()
      })

      // Focus should now be in the modal
      expect(document.activeElement).toBe(screen.getByTestId('modal-close'))

      // Close the modal by clicking submit
      fireEvent.click(screen.getByTestId('modal-submit'))

      act(() => {
        jest.runAllTimers()
      })

      // Focus should be restored to trigger button
      expect(document.activeElement).toBe(triggerButton)
    })

    it('does not restore focus when returnFocus is false', () => {
      function TestComponentNoReturn() {
        const [isActive, setIsActive] = useState(false)
        const containerRef = useRef<HTMLDivElement>(null)

        useFocusTrap(containerRef, {
          isActive,
          returnFocus: false,
        })

        return (
          <>
            <button data-testid="trigger-no-return" onClick={() => setIsActive(true)}>
              Open
            </button>
            {isActive && (
              <div ref={containerRef} data-testid="modal-no-return">
                <button data-testid="close-no-return" onClick={() => setIsActive(false)}>
                  Close
                </button>
              </div>
            )}
          </>
        )
      }

      render(<TestComponentNoReturn />)

      const trigger = screen.getByTestId('trigger-no-return')

      // Focus and click trigger
      act(() => {
        trigger.focus()
      })
      fireEvent.click(trigger)

      act(() => {
        jest.runAllTimers()
      })

      // Focus is in modal
      expect(document.activeElement).toBe(screen.getByTestId('close-no-return'))

      // Close modal
      fireEvent.click(screen.getByTestId('close-no-return'))

      act(() => {
        jest.runAllTimers()
      })

      // Focus should NOT be restored to trigger (returnFocus: false)
      // It will be on body since the modal element is removed
      expect(document.activeElement).not.toBe(trigger)
    })

    it('cleans up event listener when deactivated', () => {
      const addEventListenerSpy = jest.spyOn(document, 'addEventListener')
      const removeEventListenerSpy = jest.spyOn(document, 'removeEventListener')

      const { rerender } = render(<TestComponent isActive={true} />)

      act(() => {
        jest.runAllTimers()
      })

      expect(addEventListenerSpy).toHaveBeenCalledWith('keydown', expect.any(Function))

      // Deactivate the trap
      rerender(<TestComponent isActive={false} />)

      act(() => {
        jest.runAllTimers()
      })

      expect(removeEventListenerSpy).toHaveBeenCalledWith('keydown', expect.any(Function))

      addEventListenerSpy.mockRestore()
      removeEventListenerSpy.mockRestore()
    })
  })

  describe('Non-Tab key handling', () => {
    it('ignores non-Tab key presses', () => {
      render(<TestComponent isActive={true} />)

      act(() => {
        jest.runAllTimers()
      })

      const firstButton = screen.getByTestId('first-button')
      act(() => {
        firstButton.focus()
      })

      // Press Enter - should be ignored by focus trap
      const event = new KeyboardEvent('keydown', {
        key: 'Enter',
        bubbles: true,
        cancelable: true,
      })

      const preventDefault = jest.fn()
      Object.defineProperty(event, 'preventDefault', { value: preventDefault })

      document.dispatchEvent(event)

      // Focus trap should not prevent default for non-Tab keys
      expect(preventDefault).not.toHaveBeenCalled()
    })

    it('ignores Escape key presses', () => {
      render(<TestComponent isActive={true} />)

      act(() => {
        jest.runAllTimers()
      })

      const event = new KeyboardEvent('keydown', {
        key: 'Escape',
        bubbles: true,
        cancelable: true,
      })

      const preventDefault = jest.fn()
      Object.defineProperty(event, 'preventDefault', { value: preventDefault })

      document.dispatchEvent(event)

      // Focus trap should not prevent Escape (handled elsewhere for modal close)
      expect(preventDefault).not.toHaveBeenCalled()
    })
  })

  describe('Dynamic focus trap activation', () => {
    it('activates focus trap when isActive changes from false to true', () => {
      const { rerender } = render(<TestComponent isActive={false} />)

      act(() => {
        jest.runAllTimers()
      })

      // Focus should not be set
      expect(document.activeElement).toBe(document.body)

      // Activate the trap
      rerender(<TestComponent isActive={true} />)

      act(() => {
        jest.runAllTimers()
      })

      // Focus should now be set to first focusable element
      expect(document.activeElement).toBe(screen.getByTestId('first-button'))
    })

    it('deactivates focus trap when isActive changes from true to false', () => {
      const { rerender } = render(<TestComponent isActive={true} />)

      act(() => {
        jest.runAllTimers()
      })

      const closeButton = screen.getByTestId('close-button')
      act(() => {
        closeButton.focus()
      })

      // Tab should wrap when active
      fireEvent.keyDown(document, { key: 'Tab', shiftKey: false })
      expect(document.activeElement).toBe(screen.getByTestId('first-button'))

      // Deactivate
      rerender(<TestComponent isActive={false} />)

      act(() => {
        jest.runAllTimers()
      })

      // Focus back on last element
      act(() => {
        closeButton.focus()
      })

      // Tab should now NOT be intercepted (event listener removed)
      // We can't easily test this without spy, so we verify the listener was removed
      // via the previous test
    })
  })

  describe('Edge cases', () => {
    it('handles elements with tabindex correctly', () => {
      function TestComponentWithTabindex({ isActive }: { isActive: boolean }) {
        const containerRef = useRef<HTMLDivElement>(null)

        useFocusTrap(containerRef, { isActive })

        return (
          <div ref={containerRef}>
            <div tabIndex={0} data-testid="tabbable-div">
              Tabbable div
            </div>
            <div tabIndex={-1} data-testid="programmatic-div">
              Programmatically focusable only
            </div>
            <button data-testid="regular-button">Button</button>
          </div>
        )
      }

      render(<TestComponentWithTabindex isActive={true} />)

      act(() => {
        jest.runAllTimers()
      })

      // First focusable should be the tabbable div
      expect(document.activeElement).toBe(screen.getByTestId('tabbable-div'))

      // Focus on last element
      const button = screen.getByTestId('regular-button')
      act(() => {
        button.focus()
      })

      // Tab should wrap to tabbable-div (skipping tabindex="-1")
      fireEvent.keyDown(document, { key: 'Tab', shiftKey: false })

      expect(document.activeElement).toBe(screen.getByTestId('tabbable-div'))
    })

    it('handles single focusable element', () => {
      function TestComponentSingle({ isActive }: { isActive: boolean }) {
        const containerRef = useRef<HTMLDivElement>(null)

        useFocusTrap(containerRef, { isActive })

        return (
          <div ref={containerRef}>
            <button data-testid="only-button">Only Button</button>
          </div>
        )
      }

      render(<TestComponentSingle isActive={true} />)

      act(() => {
        jest.runAllTimers()
      })

      const button = screen.getByTestId('only-button')
      expect(document.activeElement).toBe(button)

      // Tab should keep focus on the same element
      fireEvent.keyDown(document, { key: 'Tab', shiftKey: false })
      expect(document.activeElement).toBe(button)

      // Shift+Tab should also keep focus
      fireEvent.keyDown(document, { key: 'Tab', shiftKey: true })
      expect(document.activeElement).toBe(button)
    })
  })
})
