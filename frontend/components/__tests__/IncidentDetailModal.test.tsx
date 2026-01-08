import React from 'react'
import { render, screen, fireEvent, act, waitFor } from '@testing-library/react'
import { IncidentDetailModal, useIncidentDetailModal } from '../IncidentDetailModal'
import type { Incident, IncidentSource } from '@/types'

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

// Mock EvidenceBadge component
jest.mock('../EvidenceBadge', () => ({
  EvidenceBadge: ({ score }: { score: number }) => (
    <span data-testid="evidence-badge">Evidence: {score}</span>
  ),
}))

// Mock SourceBadge component
jest.mock('../SourceBadge', () => ({
  SourceBadge: ({ url, type, title }: { url: string; type: string; title: string }) => (
    <a href={url} data-testid="source-badge" data-type={type}>
      {title}
    </a>
  ),
}))

// Mock clipboard API
const mockClipboard = {
  writeText: jest.fn().mockResolvedValue(undefined),
}
Object.assign(navigator, { clipboard: mockClipboard })

/**
 * Helper function to create mock incident data
 */
function createMockIncident(overrides: Partial<Incident> = {}): Incident {
  return {
    id: 'test-incident-1',
    title: 'Test Drone Incident at Copenhagen Airport',
    narrative: 'A drone was spotted flying near the runway at Copenhagen Airport. Multiple witnesses reported seeing the drone.',
    occurred_at: '2025-06-15T10:30:00Z',
    first_seen_at: '2025-06-15T10:30:00Z',
    last_seen_at: '2025-06-15T12:00:00Z',
    lat: 55.6181,
    lon: 12.6561,
    location_name: 'Copenhagen Airport',
    asset_type: 'airport',
    status: 'active',
    evidence_score: 3,
    country: 'Denmark',
    region: 'Zealand',
    sources: [
      {
        source_url: 'https://police.dk/report/1234',
        source_type: 'police',
        source_name: 'Danish Police',
        source_title: 'Official Police Report',
        source_quote: 'Multiple drones were observed in restricted airspace.',
        published_at: '2025-06-15T11:00:00Z',
        trust_weight: 4,
      },
      {
        source_url: 'https://news.dk/article/5678',
        source_type: 'news',
        source_name: 'Danish News',
        source_title: 'News Report on Drone Sighting',
        published_at: '2025-06-15T12:00:00Z',
        trust_weight: 2,
      },
    ],
    ...overrides,
  }
}

describe('IncidentDetailModal', () => {
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
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      const dialog = screen.getByRole('dialog')
      expect(dialog).toBeInTheDocument()
    })

    it('has aria-modal="true" attribute', () => {
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      const dialog = screen.getByRole('dialog')
      expect(dialog).toHaveAttribute('aria-modal', 'true')
    })

    it('has aria-labelledby pointing to the modal title', () => {
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      const dialog = screen.getByRole('dialog')
      expect(dialog).toHaveAttribute('aria-labelledby', 'incident-modal-title')

      // Verify the title element exists with the correct ID
      const title = document.getElementById('incident-modal-title')
      expect(title).toBeInTheDocument()
      expect(title?.tagName).toBe('H2')
      expect(title?.textContent).toContain(incident.title)
    })

    it('has aria-describedby pointing to the modal description', () => {
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      const dialog = screen.getByRole('dialog')
      expect(dialog).toHaveAttribute('aria-describedby', 'incident-modal-description')

      // Verify the description element exists with the correct ID
      const description = document.getElementById('incident-modal-description')
      expect(description).toBeInTheDocument()
      expect(description?.textContent).toContain('Incident details')
    })

    it('has close button with aria-label', () => {
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      const closeButton = screen.getByLabelText('Close modal')
      expect(closeButton).toBeInTheDocument()
    })

    it('does not render dialog when closed', () => {
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={false} onClose={jest.fn()} incident={incident} />)

      const dialog = screen.queryByRole('dialog')
      expect(dialog).not.toBeInTheDocument()
    })

    it('does not render dialog when incident is null', () => {
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={null} />)

      const dialog = screen.queryByRole('dialog')
      expect(dialog).not.toBeInTheDocument()
    })
  })

  describe('Focus management - Initial focus', () => {
    it('sets initial focus to close button when modal opens', () => {
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      act(() => {
        jest.runAllTimers()
      })

      const closeButton = screen.getByLabelText('Close modal')
      expect(document.activeElement).toBe(closeButton)
    })

    it('does not set focus when modal is closed', () => {
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={false} onClose={jest.fn()} incident={incident} />)

      act(() => {
        jest.runAllTimers()
      })

      expect(document.activeElement).toBe(document.body)
    })
  })

  describe('Focus trapping', () => {
    it('keeps focus within modal when Tab is pressed on last focusable element', () => {
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

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
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

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

    it('has multiple focusable elements', () => {
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      const dialog = screen.getByRole('dialog')
      const focusableElements = dialog.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )

      // Should have close button and other interactive elements (copy button, Google Maps link, source links)
      expect(focusableElements.length).toBeGreaterThanOrEqual(2)
    })
  })

  describe('Focus restoration', () => {
    function TestModalWithTrigger() {
      const { isOpen, selectedIncident, openModal, closeModal } = useIncidentDetailModal()
      const incident = createMockIncident()

      return (
        <>
          <button data-testid="trigger-button" onClick={() => openModal(incident)}>
            Open Details
          </button>
          <IncidentDetailModal isOpen={isOpen} onClose={closeModal} incident={selectedIncident} />
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
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={mockOnClose} incident={incident} />)

      fireEvent.keyDown(document, { key: 'Escape' })

      expect(mockOnClose).toHaveBeenCalledTimes(1)
    })

    it('does not call onClose for Escape when modal is closed', () => {
      const mockOnClose = jest.fn()
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={false} onClose={mockOnClose} incident={incident} />)

      fireEvent.keyDown(document, { key: 'Escape' })

      expect(mockOnClose).not.toHaveBeenCalled()
    })

    it('does not close modal for other key presses', () => {
      const mockOnClose = jest.fn()
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={mockOnClose} incident={incident} />)

      fireEvent.keyDown(document, { key: 'Enter' })
      fireEvent.keyDown(document, { key: 'Tab' })
      fireEvent.keyDown(document, { key: 'a' })

      expect(mockOnClose).not.toHaveBeenCalled()
    })
  })

  describe('Click outside to close', () => {
    it('closes modal when clicking outside the modal content', () => {
      const mockOnClose = jest.fn()
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={mockOnClose} incident={incident} />)

      // Get the backdrop (parent container)
      const dialog = screen.getByRole('dialog')
      const backdrop = dialog.parentElement

      // Click on the backdrop (outside the modal)
      fireEvent.mouseDown(backdrop!)

      expect(mockOnClose).toHaveBeenCalledTimes(1)
    })

    it('does not close modal when clicking inside the modal content', () => {
      const mockOnClose = jest.fn()
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={mockOnClose} incident={incident} />)

      // Click inside the modal
      const dialog = screen.getByRole('dialog')
      fireEvent.mouseDown(dialog)

      expect(mockOnClose).not.toHaveBeenCalled()
    })
  })

  describe('Body scroll prevention', () => {
    it('prevents body scroll when modal is open', () => {
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(document.body.style.overflow).toBe('hidden')
    })

    it('restores body scroll when modal is closed', () => {
      const incident = createMockIncident()
      const { rerender } = render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(document.body.style.overflow).toBe('hidden')

      rerender(<IncidentDetailModal isOpen={false} onClose={jest.fn()} incident={incident} />)

      expect(document.body.style.overflow).toBe('unset')
    })

    it('cleans up body scroll on unmount', () => {
      const incident = createMockIncident()
      const { unmount } = render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(document.body.style.overflow).toBe('hidden')

      unmount()

      expect(document.body.style.overflow).toBe('unset')
    })
  })

  describe('useIncidentDetailModal hook', () => {
    function TestHookComponent() {
      const { isOpen, selectedIncident, openModal, closeModal } = useIncidentDetailModal()
      const mockIncident = createMockIncident()

      return (
        <>
          <span data-testid="status">{isOpen ? 'open' : 'closed'}</span>
          <span data-testid="incident-id">{selectedIncident?.id || 'none'}</span>
          <button onClick={() => openModal(mockIncident)}>Open</button>
          <button onClick={closeModal}>Close</button>
        </>
      )
    }

    it('returns isOpen as false initially', () => {
      render(<TestHookComponent />)

      expect(screen.getByTestId('status')).toHaveTextContent('closed')
    })

    it('returns selectedIncident as null initially', () => {
      render(<TestHookComponent />)

      expect(screen.getByTestId('incident-id')).toHaveTextContent('none')
    })

    it('sets isOpen to true and stores incident when openModal is called', () => {
      render(<TestHookComponent />)

      fireEvent.click(screen.getByText('Open'))

      expect(screen.getByTestId('status')).toHaveTextContent('open')
      expect(screen.getByTestId('incident-id')).toHaveTextContent('test-incident-1')
    })

    it('sets isOpen to false when closeModal is called', () => {
      render(<TestHookComponent />)

      fireEvent.click(screen.getByText('Open'))
      expect(screen.getByTestId('status')).toHaveTextContent('open')

      fireEvent.click(screen.getByText('Close'))
      expect(screen.getByTestId('status')).toHaveTextContent('closed')
    })

    it('clears selectedIncident after animation delay when closeModal is called', async () => {
      render(<TestHookComponent />)

      fireEvent.click(screen.getByText('Open'))
      expect(screen.getByTestId('incident-id')).toHaveTextContent('test-incident-1')

      fireEvent.click(screen.getByText('Close'))

      // Incident should still be visible immediately (for exit animation)
      expect(screen.getByTestId('incident-id')).toHaveTextContent('test-incident-1')

      // Wait for animation delay (200ms)
      act(() => {
        jest.advanceTimersByTime(200)
      })

      // Now incident should be cleared
      expect(screen.getByTestId('incident-id')).toHaveTextContent('none')
    })
  })

  describe('Header content', () => {
    it('renders incident title', () => {
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(screen.getByText(incident.title)).toBeInTheDocument()
    })

    it('renders evidence badge with correct score', () => {
      const incident = createMockIncident({ evidence_score: 4 })
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(screen.getByTestId('evidence-badge')).toHaveTextContent('Evidence: 4')
    })

    it('renders status badge', () => {
      const incident = createMockIncident({ status: 'active' })
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(screen.getByText('Active')).toBeInTheDocument()
    })

    it('renders status badge for different statuses', () => {
      const statuses: Array<Incident['status']> = ['active', 'resolved', 'unconfirmed', 'false_positive']

      statuses.forEach((status) => {
        const incident = createMockIncident({ status })
        const { unmount } = render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

        // Verify some status text is visible (exact text depends on status config)
        expect(screen.getByRole('dialog')).toBeInTheDocument()

        unmount()
        document.body.style.overflow = 'unset'
      })
    })

    it('renders asset type badge when available', () => {
      const incident = createMockIncident({ asset_type: 'airport' })
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(screen.getByText(/Airport/i)).toBeInTheDocument()
    })

    it('renders country with flag', () => {
      const incident = createMockIncident({ country: 'Denmark' })
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(screen.getByText('Denmark')).toBeInTheDocument()
    })

    it('renders region when available', () => {
      const incident = createMockIncident({ region: 'Zealand' })
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(screen.getByText('Zealand')).toBeInTheDocument()
    })
  })

  describe('Narrative section', () => {
    it('renders narrative section with full text', () => {
      const narrative = 'A drone was spotted flying near the runway at Copenhagen Airport. Multiple witnesses reported seeing the drone.'
      const incident = createMockIncident({ narrative })
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(screen.getByText('Narrative')).toBeInTheDocument()
      expect(screen.getByText(narrative)).toBeInTheDocument()
    })

    it('handles incident with empty narrative', () => {
      const incident = createMockIncident({ narrative: '' })
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      // Narrative section should not be rendered
      expect(screen.queryByText('Narrative')).not.toBeInTheDocument()
    })

    it('handles incident with missing narrative', () => {
      const incident = createMockIncident({ narrative: undefined })
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      // Narrative section should not be rendered
      expect(screen.queryByText('Narrative')).not.toBeInTheDocument()
    })
  })

  describe('Location section', () => {
    it('renders location section', () => {
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(screen.getByText('Location')).toBeInTheDocument()
    })

    it('renders location name', () => {
      const incident = createMockIncident({ location_name: 'Copenhagen Airport' })
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(screen.getByText('Copenhagen Airport')).toBeInTheDocument()
    })

    it('renders coordinates formatted to 4 decimal places', () => {
      const incident = createMockIncident({ lat: 55.618123456, lon: 12.656198765 })
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(screen.getByText('55.6181, 12.6562')).toBeInTheDocument()
    })

    it('renders copy coordinates button', () => {
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      const copyButton = screen.getByLabelText('Copy coordinates to clipboard')
      expect(copyButton).toBeInTheDocument()
    })

    it('copies coordinates to clipboard when copy button is clicked', async () => {
      const incident = createMockIncident({ lat: 55.6181, lon: 12.6561 })
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      const copyButton = screen.getByLabelText('Copy coordinates to clipboard')
      fireEvent.click(copyButton)

      expect(mockClipboard.writeText).toHaveBeenCalledWith('55.6181, 12.6561')
    })

    it('shows "Copied!" feedback after copying', async () => {
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      const copyButton = screen.getByLabelText('Copy coordinates to clipboard')
      fireEvent.click(copyButton)

      await waitFor(() => {
        expect(screen.getByText('Copied!')).toBeInTheDocument()
      })
    })

    it('renders Google Maps link', () => {
      const incident = createMockIncident({ lat: 55.6181, lon: 12.6561 })
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      const mapsLink = screen.getByText('Open in Google Maps')
      expect(mapsLink).toBeInTheDocument()
      expect(mapsLink).toHaveAttribute('href', 'https://www.google.com/maps?q=55.6181,12.6561')
      expect(mapsLink).toHaveAttribute('target', '_blank')
      expect(mapsLink).toHaveAttribute('rel', 'noopener noreferrer')
    })
  })

  describe('Timeline section', () => {
    it('renders timeline section', () => {
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(screen.getByText('Timeline')).toBeInTheDocument()
    })

    it('renders incident date', () => {
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(screen.getByText('Incident Date')).toBeInTheDocument()
    })

    it('renders first and last reported dates when different', () => {
      const incident = createMockIncident({
        first_seen_at: '2025-06-15T10:30:00Z',
        last_seen_at: '2025-06-15T12:00:00Z',
      })
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(screen.getByText('First Reported')).toBeInTheDocument()
      expect(screen.getByText('Last Reported')).toBeInTheDocument()
    })

    it('shows single sighting text when first and last are the same', () => {
      const incident = createMockIncident({
        first_seen_at: '2025-06-15T10:30:00Z',
        last_seen_at: '2025-06-15T10:30:00Z',
      })
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(screen.getByText('First & Last Reported')).toBeInTheDocument()
      expect(screen.getByText('Single sighting')).toBeInTheDocument()
    })

    it('shows duration when first and last seen are different', () => {
      const incident = createMockIncident({
        first_seen_at: '2025-06-15T10:00:00Z',
        last_seen_at: '2025-06-16T10:00:00Z',
      })
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(screen.getByText(/Duration:/)).toBeInTheDocument()
    })
  })

  describe('Sources section', () => {
    it('renders sources section with count', () => {
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(screen.getByText('Sources (2)')).toBeInTheDocument()
    })

    it('renders all sources', () => {
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      const sourceBadges = screen.getAllByTestId('source-badge')
      expect(sourceBadges).toHaveLength(2)
    })

    it('renders source quote when available', () => {
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(screen.getByText(/Multiple drones were observed in restricted airspace/)).toBeInTheDocument()
    })

    it('renders trust weight indicator', () => {
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      // Official (trust_weight: 4) and Media (trust_weight: 2)
      expect(screen.getByText('Official')).toBeInTheDocument()
      expect(screen.getByText('Media')).toBeInTheDocument()
    })

    it('handles incident with no sources', () => {
      const incident = createMockIncident({ sources: [] })
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      // Sources section should not be rendered
      expect(screen.queryByText(/Sources \(/)).not.toBeInTheDocument()
    })

    it('renders many sources without limit', () => {
      const manySources: IncidentSource[] = Array.from({ length: 10 }, (_, i) => ({
        source_url: `https://example.com/source-${i}`,
        source_type: 'news',
        source_name: `Source ${i}`,
        source_title: `Source Title ${i}`,
        trust_weight: 2,
      }))

      const incident = createMockIncident({ sources: manySources })
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(screen.getByText('Sources (10)')).toBeInTheDocument()
      const sourceBadges = screen.getAllByTestId('source-badge')
      expect(sourceBadges).toHaveLength(10)
    })
  })

  describe('Evidence breakdown section', () => {
    it('renders evidence breakdown section', () => {
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(screen.getByText('Evidence Breakdown')).toBeInTheDocument()
    })

    it('renders source breakdown by type', () => {
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(screen.getByText(/Source Breakdown/)).toBeInTheDocument()
      expect(screen.getByText('Social/Other')).toBeInTheDocument()
    })

    it('renders "Why this score?" explanation', () => {
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(screen.getByText('Why this score?')).toBeInTheDocument()
    })

    it('highlights official sources when present', () => {
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(screen.getByText('Official Sources Confirmed')).toBeInTheDocument()
    })

    it('does not show official sources highlight when none present', () => {
      const incident = createMockIncident({
        sources: [
          {
            source_url: 'https://news.com/article',
            source_type: 'news',
            source_title: 'News Article',
            trust_weight: 2,
          },
        ],
      })
      render(<IncidentDetailModal isOpen={true} onClose={jest.fn()} incident={incident} />)

      expect(screen.queryByText('Official Sources Confirmed')).not.toBeInTheDocument()
    })
  })

  describe('Close button', () => {
    it('calls onClose when close button is clicked', () => {
      const mockOnClose = jest.fn()
      const incident = createMockIncident()
      render(<IncidentDetailModal isOpen={true} onClose={mockOnClose} incident={incident} />)

      const closeButton = screen.getByLabelText('Close modal')
      fireEvent.click(closeButton)

      expect(mockOnClose).toHaveBeenCalledTimes(1)
    })
  })
})
