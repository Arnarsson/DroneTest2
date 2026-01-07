import React, { useRef, useState } from 'react'
import { render, screen, fireEvent, act, waitFor } from '@testing-library/react'
import { AboutModal, useAboutModal } from '../AboutModal'

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: React.forwardRef(
      (
        { children, className, role, 'aria-modal': ariaModal, 'aria-labelledby': ariaLabelledby, 'aria-describedby': ariaDescribedby, ...props }: any,
        ref: React.Ref<HTMLDivElement>
      ) => (
        <div
          ref={ref}
          className={className}
          role={role}
          aria-modal={ariaModal}
          aria-labelledby={ariaLabelledby}
          aria-describedby={ariaDescribedby}
          {...props}
        >
          {children}
        </div>
      )
    ),
    button: ({ children, onClick, className, ...props }: any) => (
      <button onClick={onClick} className={className} {...props}>
        {children}
      </button>
    ),
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}))

// Mock the DroneWatchLogo component
jest.mock('../DroneWatchLogo', () => ({
  DroneWatchLogo: () => <div data-testid="logo">Logo</div>,
}))

describe('AboutModal', () => {
  beforeEach(() => {
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.useRealTimers()
    jest.clearAllMocks()
    // Reset body overflow
    document.body.style.overflow = 'unset'
  })

  describe('ARIA attributes', () => {
    it('renders with role="dialog"', () => {
      render(<AboutModal isOpen={true} onClose={jest.fn()} />)

      const dialog = screen.getByRole('dialog')
      expect(dialog).toBeInTheDocument()
    })

    it('has aria-modal="true" attribute', () => {
      render(<AboutModal isOpen={true} onClose={jest.fn()} />)

      const dialog = screen.getByRole('dialog')
      expect(dialog).toHaveAttribute('aria-modal', 'true')
    })

    it('has aria-labelledby pointing to the modal title', () => {
      render(<AboutModal isOpen={true} onClose={jest.fn()} />)

      const dialog = screen.getByRole('dialog')
      expect(dialog).toHaveAttribute('aria-labelledby', 'about-modal-title')

      // Verify the title element exists with the correct ID
      const title = document.getElementById('about-modal-title')
      expect(title).toBeInTheDocument()
      expect(title?.tagName).toBe('H2')
      expect(title?.textContent).toBe('DroneWatch')
    })

    it('has aria-describedby pointing to the modal description', () => {
      render(<AboutModal isOpen={true} onClose={jest.fn()} />)

      const dialog = screen.getByRole('dialog')
      expect(dialog).toHaveAttribute('aria-describedby', 'about-modal-description')

      // Verify the description element exists with the correct ID
      const description = document.getElementById('about-modal-description')
      expect(description).toBeInTheDocument()
      expect(description?.textContent).toBe('Safety Through Transparency')
    })

    it('has close button with aria-label', () => {
      render(<AboutModal isOpen={true} onClose={jest.fn()} />)

      const closeButton = screen.getByLabelText('Close modal')
      expect(closeButton).toBeInTheDocument()
    })

    it('does not render dialog when closed', () => {
      render(<AboutModal isOpen={false} onClose={jest.fn()} />)

      const dialog = screen.queryByRole('dialog')
      expect(dialog).not.toBeInTheDocument()
    })
  })

  describe('Focus management - Initial focus', () => {
    it('sets initial focus to close button when modal opens', () => {
      render(<AboutModal isOpen={true} onClose={jest.fn()} />)

      act(() => {
        jest.runAllTimers()
      })

      const closeButton = screen.getByLabelText('Close modal')
      expect(document.activeElement).toBe(closeButton)
    })

    it('does not set focus when modal is closed', () => {
      render(<AboutModal isOpen={false} onClose={jest.fn()} />)

      act(() => {
        jest.runAllTimers()
      })

      expect(document.activeElement).toBe(document.body)
    })
  })

  describe('Focus trapping', () => {
    it('keeps focus within modal when Tab is pressed on last focusable element', () => {
      render(<AboutModal isOpen={true} onClose={jest.fn()} />)

      act(() => {
        jest.runAllTimers()
      })

      // Get all focusable elements
      const dialog = screen.getByRole('dialog')
      const focusableElements = dialog.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
      const lastFocusable = focusableElements[focusableElements.length - 1] as HTMLElement
      const firstFocusable = focusableElements[0] as HTMLElement

      // Focus the last focusable element
      act(() => {
        lastFocusable.focus()
      })
      expect(document.activeElement).toBe(lastFocusable)

      // Press Tab - should wrap to first element
      fireEvent.keyDown(document, { key: 'Tab', shiftKey: false })

      expect(document.activeElement).toBe(firstFocusable)
    })

    it('keeps focus within modal when Shift+Tab is pressed on first focusable element', () => {
      render(<AboutModal isOpen={true} onClose={jest.fn()} />)

      act(() => {
        jest.runAllTimers()
      })

      // Get all focusable elements
      const dialog = screen.getByRole('dialog')
      const focusableElements = dialog.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
      const firstFocusable = focusableElements[0] as HTMLElement
      const lastFocusable = focusableElements[focusableElements.length - 1] as HTMLElement

      // Focus the first focusable element
      act(() => {
        firstFocusable.focus()
      })
      expect(document.activeElement).toBe(firstFocusable)

      // Press Shift+Tab - should wrap to last element
      fireEvent.keyDown(document, { key: 'Tab', shiftKey: true })

      expect(document.activeElement).toBe(lastFocusable)
    })

    it('has multiple focusable elements (close button and GitHub link)', () => {
      render(<AboutModal isOpen={true} onClose={jest.fn()} />)

      const dialog = screen.getByRole('dialog')
      const focusableElements = dialog.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )

      // Should have close button and at least the GitHub link
      expect(focusableElements.length).toBeGreaterThanOrEqual(2)
    })
  })

  describe('Focus restoration', () => {
    function TestModalWithTrigger() {
      const { isOpen, openModal, closeModal } = useAboutModal()

      return (
        <>
          <button data-testid="trigger-button" onClick={openModal}>
            Open About
          </button>
          <AboutModal isOpen={isOpen} onClose={closeModal} />
        </>
      )
    }

    it('restores focus to trigger element when modal closes', () => {
      render(<TestModalWithTrigger />)

      const triggerButton = screen.getByTestId('trigger-button')

      // Focus and click the trigger button
      act(() => {
        triggerButton.focus()
      })
      expect(document.activeElement).toBe(triggerButton)

      // Open the modal
      fireEvent.click(triggerButton)

      act(() => {
        jest.runAllTimers()
      })

      // Focus should be on the close button in the modal
      const closeButton = screen.getByLabelText('Close modal')
      expect(document.activeElement).toBe(closeButton)

      // Close the modal by clicking close button
      fireEvent.click(closeButton)

      act(() => {
        jest.runAllTimers()
      })

      // Focus should be restored to trigger button
      expect(document.activeElement).toBe(triggerButton)
    })

    it('restores focus when modal is closed via Escape key', () => {
      render(<TestModalWithTrigger />)

      const triggerButton = screen.getByTestId('trigger-button')

      // Focus and click the trigger button
      act(() => {
        triggerButton.focus()
      })

      // Open the modal
      fireEvent.click(triggerButton)

      act(() => {
        jest.runAllTimers()
      })

      // Modal should be open
      expect(screen.getByRole('dialog')).toBeInTheDocument()

      // Close via Escape key
      fireEvent.keyDown(document, { key: 'Escape' })

      act(() => {
        jest.runAllTimers()
      })

      // Modal should be closed
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()

      // Focus should be restored to trigger button
      expect(document.activeElement).toBe(triggerButton)
    })
  })

  describe('Keyboard interaction', () => {
    it('closes modal when Escape key is pressed', () => {
      const mockOnClose = jest.fn()
      render(<AboutModal isOpen={true} onClose={mockOnClose} />)

      fireEvent.keyDown(document, { key: 'Escape' })

      expect(mockOnClose).toHaveBeenCalledTimes(1)
    })

    it('does not call onClose for Escape when modal is closed', () => {
      const mockOnClose = jest.fn()
      render(<AboutModal isOpen={false} onClose={mockOnClose} />)

      fireEvent.keyDown(document, { key: 'Escape' })

      expect(mockOnClose).not.toHaveBeenCalled()
    })

    it('does not close modal for other key presses', () => {
      const mockOnClose = jest.fn()
      render(<AboutModal isOpen={true} onClose={mockOnClose} />)

      fireEvent.keyDown(document, { key: 'Enter' })
      fireEvent.keyDown(document, { key: 'Tab' })
      fireEvent.keyDown(document, { key: 'a' })

      expect(mockOnClose).not.toHaveBeenCalled()
    })
  })

  describe('Click outside to close', () => {
    it('closes modal when clicking outside the modal content', () => {
      const mockOnClose = jest.fn()
      render(<AboutModal isOpen={true} onClose={mockOnClose} />)

      // Get the backdrop (parent container)
      const dialog = screen.getByRole('dialog')
      const backdrop = dialog.parentElement

      // Click on the backdrop (outside the modal)
      fireEvent.mouseDown(backdrop!)

      expect(mockOnClose).toHaveBeenCalledTimes(1)
    })

    it('does not close modal when clicking inside the modal content', () => {
      const mockOnClose = jest.fn()
      render(<AboutModal isOpen={true} onClose={mockOnClose} />)

      // Click inside the modal
      const dialog = screen.getByRole('dialog')
      fireEvent.mouseDown(dialog)

      expect(mockOnClose).not.toHaveBeenCalled()
    })
  })

  describe('Body scroll prevention', () => {
    it('prevents body scroll when modal is open', () => {
      render(<AboutModal isOpen={true} onClose={jest.fn()} />)

      expect(document.body.style.overflow).toBe('hidden')
    })

    it('restores body scroll when modal is closed', () => {
      const { rerender } = render(<AboutModal isOpen={true} onClose={jest.fn()} />)

      expect(document.body.style.overflow).toBe('hidden')

      rerender(<AboutModal isOpen={false} onClose={jest.fn()} />)

      expect(document.body.style.overflow).toBe('unset')
    })

    it('cleans up body scroll on unmount', () => {
      const { unmount } = render(<AboutModal isOpen={true} onClose={jest.fn()} />)

      expect(document.body.style.overflow).toBe('hidden')

      unmount()

      expect(document.body.style.overflow).toBe('unset')
    })
  })

  describe('useAboutModal hook', () => {
    function TestHookComponent() {
      const { isOpen, openModal, closeModal } = useAboutModal()

      return (
        <>
          <span data-testid="status">{isOpen ? 'open' : 'closed'}</span>
          <button onClick={openModal}>Open</button>
          <button onClick={closeModal}>Close</button>
        </>
      )
    }

    it('returns isOpen as false initially', () => {
      render(<TestHookComponent />)

      expect(screen.getByTestId('status')).toHaveTextContent('closed')
    })

    it('sets isOpen to true when openModal is called', () => {
      render(<TestHookComponent />)

      fireEvent.click(screen.getByText('Open'))

      expect(screen.getByTestId('status')).toHaveTextContent('open')
    })

    it('sets isOpen to false when closeModal is called', () => {
      render(<TestHookComponent />)

      fireEvent.click(screen.getByText('Open'))
      expect(screen.getByTestId('status')).toHaveTextContent('open')

      fireEvent.click(screen.getByText('Close'))
      expect(screen.getByTestId('status')).toHaveTextContent('closed')
    })
  })

  describe('Modal content', () => {
    it('renders modal title', () => {
      render(<AboutModal isOpen={true} onClose={jest.fn()} />)

      expect(screen.getByText('DroneWatch')).toBeInTheDocument()
    })

    it('renders modal description', () => {
      render(<AboutModal isOpen={true} onClose={jest.fn()} />)

      expect(screen.getByText('Safety Through Transparency')).toBeInTheDocument()
    })

    it('renders mission section', () => {
      render(<AboutModal isOpen={true} onClose={jest.fn()} />)

      expect(screen.getByText('Our Mission')).toBeInTheDocument()
    })

    it('renders evidence system section', () => {
      render(<AboutModal isOpen={true} onClose={jest.fn()} />)

      expect(screen.getByText('Evidence-Based Verification')).toBeInTheDocument()
      expect(screen.getByText('Official')).toBeInTheDocument()
      expect(screen.getByText('Verified')).toBeInTheDocument()
      expect(screen.getByText('Reported')).toBeInTheDocument()
      expect(screen.getByText('Unconfirmed')).toBeInTheDocument()
    })

    it('renders GitHub link', () => {
      render(<AboutModal isOpen={true} onClose={jest.fn()} />)

      const githubLink = screen.getByRole('link', { name: /github/i })
      expect(githubLink).toBeInTheDocument()
      expect(githubLink).toHaveAttribute('href', 'https://github.com/Arnarsson/DroneWatch2.0')
      expect(githubLink).toHaveAttribute('target', '_blank')
      expect(githubLink).toHaveAttribute('rel', 'noopener noreferrer')
    })
  })
})
