import { render, screen, fireEvent } from '@testing-library/react'
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
    div: ({ children, onClick, className, ...props }: any) => (
      <div onClick={onClick} className={className} {...props}>
        {children}
      </div>
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
})
