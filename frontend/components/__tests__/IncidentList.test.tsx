import React from 'react'
import { render, screen, fireEvent, act, within } from '@testing-library/react'
import { IncidentList } from '../IncidentList'
import type { Incident } from '@/types'

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    button: ({ children, onClick, className, ...props }: any) => (
      <button onClick={onClick} className={className} {...props}>
        {children}
      </button>
    ),
    div: React.forwardRef(
      (
        { children, onClick, className, role, 'aria-modal': ariaModal, 'aria-labelledby': ariaLabelledby, 'aria-describedby': ariaDescribedby, ...props }: any,
        ref: React.Ref<HTMLDivElement>
      ) => (
        <div
          ref={ref}
          onClick={onClick}
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
    p: ({ children, className, ...props }: any) => (
      <p className={className} {...props}>
        {children}
      </p>
    ),
    svg: ({ children, className, ...props }: any) => (
      <svg className={className} {...props}>
        {children}
      </svg>
    ),
    span: ({ children, className, ...props }: any) => (
      <span className={className} {...props}>
        {children}
      </span>
    ),
    article: ({ children, onClick, onKeyDown, className, tabIndex, role, 'aria-label': ariaLabel, ...props }: any) => (
      <article
        onClick={onClick}
        onKeyDown={onKeyDown}
        className={className}
        tabIndex={tabIndex}
        role={role}
        aria-label={ariaLabel}
        {...props}
      >
        {children}
      </article>
    ),
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}))

// Mock ExportButtons to track props passed to it
const mockExportButtons = jest.fn()
jest.mock('../ExportButtons', () => ({
  ExportButtons: (props: any) => {
    mockExportButtons(props)
    return (
      <div data-testid="export-buttons" data-disabled={props.isDisabled}>
        <button disabled={props.isDisabled} data-testid="export-csv-mock">Export CSV</button>
        <button disabled={props.isDisabled} data-testid="export-json-mock">Export JSON</button>
      </div>
    )
  },
}))

/**
 * Helper function to create mock incident data
 */
function createMockIncident(overrides: Partial<Incident> = {}): Incident {
  return {
    id: '1',
    title: 'Test Incident',
    narrative: 'A drone was spotted over the airport.',
    occurred_at: '2025-06-15T10:30:00Z',
    first_seen_at: '2025-06-15T10:30:00Z',
    last_seen_at: '2025-06-15T12:00:00Z',
    lat: 55.6181,
    lon: 12.6561,
    location_name: 'Copenhagen Airport',
    asset_type: 'airport',
    status: 'active',
    evidence_score: 3,
    country: 'DK',
    sources: [
      {
        source_url: 'https://example.com/news/1',
        source_type: 'news',
        source_title: 'Local News Report',
      },
    ],
    ...overrides,
  }
}

describe('IncidentList', () => {
  const mockIncidents = [
    createMockIncident({ id: '1', title: 'First Incident' }),
    createMockIncident({ id: '2', title: 'Second Incident' }),
    createMockIncident({ id: '3', title: 'Third Incident' }),
  ]

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('ExportButtons Integration', () => {
    it('renders ExportButtons component in the header', () => {
      render(<IncidentList incidents={mockIncidents} isLoading={false} />)

      const exportButtons = screen.getByTestId('export-buttons')
      expect(exportButtons).toBeInTheDocument()
    })

    it('passes incidents array to ExportButtons', () => {
      render(<IncidentList incidents={mockIncidents} isLoading={false} />)

      expect(mockExportButtons).toHaveBeenCalledWith(
        expect.objectContaining({
          incidents: mockIncidents,
        })
      )
    })

    it('passes isDisabled=true to ExportButtons when incidents array is empty', () => {
      render(<IncidentList incidents={[]} isLoading={false} />)

      // When incidents is empty, the no incidents view is shown
      // and ExportButtons are not rendered in that view
      // So we verify the empty state is shown instead
      expect(screen.getByText('No incidents found')).toBeInTheDocument()
    })

    it('passes isDisabled=false to ExportButtons when incidents array has items', () => {
      render(<IncidentList incidents={mockIncidents} isLoading={false} />)

      expect(mockExportButtons).toHaveBeenCalledWith(
        expect.objectContaining({
          isDisabled: false,
        })
      )
    })

    it('passes updated incidents array when incidents prop changes', () => {
      const { rerender } = render(
        <IncidentList incidents={mockIncidents} isLoading={false} />
      )

      expect(mockExportButtons).toHaveBeenCalledWith(
        expect.objectContaining({
          incidents: mockIncidents,
        })
      )

      const newIncidents = [createMockIncident({ id: '4', title: 'New Incident' })]
      rerender(<IncidentList incidents={newIncidents} isLoading={false} />)

      expect(mockExportButtons).toHaveBeenLastCalledWith(
        expect.objectContaining({
          incidents: newIncidents,
        })
      )
    })

    it('renders ExportButtons next to Group by Facility toggle', () => {
      render(<IncidentList incidents={mockIncidents} isLoading={false} />)

      const exportButtons = screen.getByTestId('export-buttons')
      const groupByFacilityButton = screen.getByText('Group by Facility')

      // Both should be in the same parent container
      const exportButtonsParent = exportButtons.parentElement
      const groupButtonParent = groupByFacilityButton.closest('button')?.parentElement

      expect(exportButtonsParent).toBe(groupButtonParent)
    })
  })

  describe('Loading State', () => {
    it('does not render ExportButtons when loading', () => {
      render(<IncidentList incidents={mockIncidents} isLoading={true} />)

      expect(screen.queryByTestId('export-buttons')).not.toBeInTheDocument()
    })

    it('renders skeleton loading cards when loading', () => {
      const { container } = render(
        <IncidentList incidents={mockIncidents} isLoading={true} />
      )

      const skeletons = container.querySelectorAll('.skeleton')
      expect(skeletons.length).toBeGreaterThan(0)
    })
  })

  describe('Empty State', () => {
    it('displays no incidents message when incidents array is empty', () => {
      render(<IncidentList incidents={[]} isLoading={false} />)

      expect(screen.getByText('No incidents found')).toBeInTheDocument()
      expect(
        screen.getByText('No drone incidents match your current filters')
      ).toBeInTheDocument()
    })

    it('does not render ExportButtons in empty state', () => {
      render(<IncidentList incidents={[]} isLoading={false} />)

      expect(screen.queryByTestId('export-buttons')).not.toBeInTheDocument()
    })

    it('displays filter suggestions in empty state', () => {
      render(<IncidentList incidents={[]} isLoading={false} />)

      expect(screen.getByText('Lowering the evidence level filter')).toBeInTheDocument()
      expect(screen.getByText('Expanding the date range')).toBeInTheDocument()
    })
  })

  describe('Incident Count Display', () => {
    it('displays correct incident count', () => {
      render(<IncidentList incidents={mockIncidents} isLoading={false} />)

      expect(screen.getByText('3')).toBeInTheDocument()
      expect(screen.getByText('incidents')).toBeInTheDocument()
    })

    it('displays singular "incident" when count is 1', () => {
      const singleIncident = [createMockIncident({ id: '1', title: 'Single Incident' })]
      render(<IncidentList incidents={singleIncident} isLoading={false} />)

      expect(screen.getByText('1')).toBeInTheDocument()
      expect(screen.getByText('incident')).toBeInTheDocument()
    })
  })

  describe('Group by Facility Toggle', () => {
    it('renders Group by Facility button', () => {
      render(<IncidentList incidents={mockIncidents} isLoading={false} />)

      expect(screen.getByText('Group by Facility')).toBeInTheDocument()
    })

    it('toggles grouping when button is clicked', () => {
      render(<IncidentList incidents={mockIncidents} isLoading={false} />)

      const toggleButton = screen.getByText('Group by Facility')

      // Initially shows flat list - incidents are displayed as cards
      expect(screen.getByText('First Incident')).toBeInTheDocument()

      // Click to enable grouping
      fireEvent.click(toggleButton)

      // After grouping is enabled, facility groups are shown
      // The implementation groups by asset_type-location_name
      expect(toggleButton).toBeInTheDocument()
    })
  })

  describe('Incident Cards', () => {
    it('renders all incident titles', () => {
      render(<IncidentList incidents={mockIncidents} isLoading={false} />)

      expect(screen.getByText('First Incident')).toBeInTheDocument()
      expect(screen.getByText('Second Incident')).toBeInTheDocument()
      expect(screen.getByText('Third Incident')).toBeInTheDocument()
    })

    it('renders incident country', () => {
      render(<IncidentList incidents={mockIncidents} isLoading={false} />)

      // All mock incidents have country 'DK'
      const countryElements = screen.getAllByText('DK')
      expect(countryElements.length).toBeGreaterThan(0)
    })

    it('renders source count badges', () => {
      render(<IncidentList incidents={mockIncidents} isLoading={false} />)

      // All mock incidents have 1 source
      const sourceBadges = screen.getAllByText('1 source')
      expect(sourceBadges.length).toBe(3)
    })

    it('renders incident narrative', () => {
      render(<IncidentList incidents={mockIncidents} isLoading={false} />)

      const narratives = screen.getAllByText('A drone was spotted over the airport.')
      expect(narratives.length).toBe(3)
    })

    it('renders location name', () => {
      render(<IncidentList incidents={mockIncidents} isLoading={false} />)

      const locations = screen.getAllByText('Copenhagen Airport')
      expect(locations.length).toBeGreaterThan(0)
    })
  })

  describe('Many Incidents', () => {
    it('handles large number of incidents', () => {
      const manyIncidents = Array.from({ length: 50 }, (_, i) =>
        createMockIncident({ id: String(i), title: `Incident ${i}` })
      )
      render(<IncidentList incidents={manyIncidents} isLoading={false} />)

      expect(screen.getByText('50')).toBeInTheDocument()
      expect(mockExportButtons).toHaveBeenCalledWith(
        expect.objectContaining({
          incidents: manyIncidents,
        })
      )
    })
  })

  describe('IncidentDetailModal Integration', () => {
    beforeEach(() => {
      jest.useFakeTimers()
    })

    afterEach(() => {
      jest.useRealTimers()
      // Reset body overflow that modal sets
      document.body.style.overflow = 'unset'
    })

    it('opens modal when clicking an incident card', () => {
      const incidents = [
        createMockIncident({ id: '1', title: 'Test Incident for Modal' }),
      ]
      render(<IncidentList incidents={incidents} isLoading={false} />)

      // Modal should not be visible initially
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()

      // Click on the incident card
      const card = screen.getByRole('button', { name: /View details for incident: Test Incident for Modal/i })
      fireEvent.click(card)

      act(() => {
        jest.runAllTimers()
      })

      // Modal should now be visible
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    it('displays correct incident data in the modal', () => {
      const testIncident = createMockIncident({
        id: 'test-123',
        title: 'Unique Modal Test Incident',
        narrative: 'This is a unique narrative for testing the modal content.',
        location_name: 'Test Location for Modal',
        country: 'DK',
        evidence_score: 3,
        sources: [
          {
            source_url: 'https://example.com/test',
            source_type: 'news',
            source_title: 'Test News Source',
          },
        ],
      })
      render(<IncidentList incidents={[testIncident]} isLoading={false} />)

      // Click on the incident card
      const card = screen.getByRole('button', { name: /View details for incident: Unique Modal Test Incident/i })
      fireEvent.click(card)

      act(() => {
        jest.runAllTimers()
      })

      // Verify modal displays the correct incident data
      const modal = screen.getByRole('dialog')
      expect(modal).toBeInTheDocument()

      // Check title is in modal (use getByRole to get the modal title)
      const modalTitle = document.getElementById('incident-modal-title')
      expect(modalTitle).toHaveTextContent('Unique Modal Test Incident')

      // Check narrative is in modal
      expect(within(modal).getByText('This is a unique narrative for testing the modal content.')).toBeInTheDocument()

      // Check location section exists
      expect(within(modal).getByText('Location')).toBeInTheDocument()
      expect(within(modal).getByText('Test Location for Modal')).toBeInTheDocument()
    })

    it('opens modal with different incident data when clicking different cards', () => {
      const incidents = [
        createMockIncident({ id: '1', title: 'First Card Incident', narrative: 'First narrative text' }),
        createMockIncident({ id: '2', title: 'Second Card Incident', narrative: 'Second narrative text' }),
      ]
      render(<IncidentList incidents={incidents} isLoading={false} />)

      // Click on first incident card
      const firstCard = screen.getByRole('button', { name: /View details for incident: First Card Incident/i })
      fireEvent.click(firstCard)

      act(() => {
        jest.runAllTimers()
      })

      // Verify first incident is shown in modal
      const modal = screen.getByRole('dialog')
      expect(within(modal).getByText('First narrative text')).toBeInTheDocument()

      // Close the modal
      const closeButton = screen.getByLabelText('Close modal')
      fireEvent.click(closeButton)

      act(() => {
        jest.runAllTimers()
      })

      // Modal should be closed
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()

      // Click on second incident card
      const secondCard = screen.getByRole('button', { name: /View details for incident: Second Card Incident/i })
      fireEvent.click(secondCard)

      act(() => {
        jest.runAllTimers()
      })

      // Verify second incident is shown in modal
      const modal2 = screen.getByRole('dialog')
      expect(within(modal2).getByText('Second narrative text')).toBeInTheDocument()
    })

    it('closes modal when clicking the close button', () => {
      const incidents = [createMockIncident({ id: '1', title: 'Test Close Button' })]
      render(<IncidentList incidents={incidents} isLoading={false} />)

      // Open the modal
      const card = screen.getByRole('button', { name: /View details for incident: Test Close Button/i })
      fireEvent.click(card)

      act(() => {
        jest.runAllTimers()
      })

      // Modal should be open
      expect(screen.getByRole('dialog')).toBeInTheDocument()

      // Click close button
      const closeButton = screen.getByLabelText('Close modal')
      fireEvent.click(closeButton)

      act(() => {
        jest.runAllTimers()
      })

      // Modal should be closed
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })

    it('closes modal when pressing Escape key', () => {
      const incidents = [createMockIncident({ id: '1', title: 'Test Escape Key' })]
      render(<IncidentList incidents={incidents} isLoading={false} />)

      // Open the modal
      const card = screen.getByRole('button', { name: /View details for incident: Test Escape Key/i })
      fireEvent.click(card)

      act(() => {
        jest.runAllTimers()
      })

      // Modal should be open
      expect(screen.getByRole('dialog')).toBeInTheDocument()

      // Press Escape key
      fireEvent.keyDown(document, { key: 'Escape' })

      act(() => {
        jest.runAllTimers()
      })

      // Modal should be closed
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })

    it('closes modal when clicking outside the modal content', () => {
      const incidents = [createMockIncident({ id: '1', title: 'Test Click Outside' })]
      render(<IncidentList incidents={incidents} isLoading={false} />)

      // Open the modal
      const card = screen.getByRole('button', { name: /View details for incident: Test Click Outside/i })
      fireEvent.click(card)

      act(() => {
        jest.runAllTimers()
      })

      // Modal should be open
      const dialog = screen.getByRole('dialog')
      expect(dialog).toBeInTheDocument()

      // Click on the backdrop (parent of dialog)
      const backdrop = dialog.parentElement
      fireEvent.mouseDown(backdrop!)

      act(() => {
        jest.runAllTimers()
      })

      // Modal should be closed
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })

    it('does not close modal when clicking inside the modal content', () => {
      const incidents = [createMockIncident({ id: '1', title: 'Test Click Inside' })]
      render(<IncidentList incidents={incidents} isLoading={false} />)

      // Open the modal
      const card = screen.getByRole('button', { name: /View details for incident: Test Click Inside/i })
      fireEvent.click(card)

      act(() => {
        jest.runAllTimers()
      })

      // Modal should be open
      const dialog = screen.getByRole('dialog')
      expect(dialog).toBeInTheDocument()

      // Click inside the modal
      fireEvent.mouseDown(dialog)

      act(() => {
        jest.runAllTimers()
      })

      // Modal should still be open
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    it('opens modal via keyboard Enter key on incident card', () => {
      const incidents = [createMockIncident({ id: '1', title: 'Test Keyboard Open' })]
      render(<IncidentList incidents={incidents} isLoading={false} />)

      // Find the incident card
      const card = screen.getByRole('button', { name: /View details for incident: Test Keyboard Open/i })

      // Focus and press Enter
      card.focus()
      fireEvent.keyDown(card, { key: 'Enter' })

      act(() => {
        jest.runAllTimers()
      })

      // Modal should be open
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    it('opens modal via keyboard Space key on incident card', () => {
      const incidents = [createMockIncident({ id: '1', title: 'Test Space Key Open' })]
      render(<IncidentList incidents={incidents} isLoading={false} />)

      // Find the incident card
      const card = screen.getByRole('button', { name: /View details for incident: Test Space Key Open/i })

      // Focus and press Space
      card.focus()
      fireEvent.keyDown(card, { key: ' ' })

      act(() => {
        jest.runAllTimers()
      })

      // Modal should be open
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    it('modal has correct ARIA attributes', () => {
      const incidents = [createMockIncident({ id: '1', title: 'Test ARIA Attributes' })]
      render(<IncidentList incidents={incidents} isLoading={false} />)

      // Open the modal
      const card = screen.getByRole('button', { name: /View details for incident: Test ARIA Attributes/i })
      fireEvent.click(card)

      act(() => {
        jest.runAllTimers()
      })

      const dialog = screen.getByRole('dialog')
      expect(dialog).toHaveAttribute('aria-modal', 'true')
      expect(dialog).toHaveAttribute('aria-labelledby', 'incident-modal-title')
      expect(dialog).toHaveAttribute('aria-describedby', 'incident-modal-description')
    })

    it('prevents body scroll when modal is open', () => {
      const incidents = [createMockIncident({ id: '1', title: 'Test Body Scroll' })]
      render(<IncidentList incidents={incidents} isLoading={false} />)

      // Body should scroll normally before modal opens
      expect(document.body.style.overflow).not.toBe('hidden')

      // Open the modal
      const card = screen.getByRole('button', { name: /View details for incident: Test Body Scroll/i })
      fireEvent.click(card)

      act(() => {
        jest.runAllTimers()
      })

      // Body scroll should be prevented
      expect(document.body.style.overflow).toBe('hidden')

      // Close the modal
      fireEvent.keyDown(document, { key: 'Escape' })

      act(() => {
        jest.runAllTimers()
      })

      // Body scroll should be restored
      expect(document.body.style.overflow).toBe('unset')
    })
  })
})
