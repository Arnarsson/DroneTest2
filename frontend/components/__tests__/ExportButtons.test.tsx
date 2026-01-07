import { render, screen, fireEvent } from '@testing-library/react'
import { ExportButtons } from '../ExportButtons'
import type { Incident } from '@/types'

// Mock the export utilities module for isolation
jest.mock('@/lib/export', () => ({
  formatIncidentsToCSV: jest.fn().mockReturnValue('mock-csv-content'),
  formatIncidentsToJSON: jest.fn().mockReturnValue('{"mock": "json"}'),
  downloadFile: jest.fn(),
  generateExportFilename: jest.fn().mockImplementation((ext: string) => `dronewatch-incidents-2025-06-15.${ext}`),
}))

// Import mocked functions for assertions
import {
  formatIncidentsToCSV,
  formatIncidentsToJSON,
  downloadFile,
  generateExportFilename,
} from '@/lib/export'

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

describe('ExportButtons', () => {
  const mockIncidents = [
    createMockIncident({ id: '1', title: 'First Incident' }),
    createMockIncident({ id: '2', title: 'Second Incident' }),
  ]

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Rendering', () => {
    it('renders both CSV and JSON export buttons', () => {
      render(<ExportButtons incidents={mockIncidents} />)

      expect(screen.getByText('Export CSV')).toBeInTheDocument()
      expect(screen.getByText('Export JSON')).toBeInTheDocument()
    })

    it('renders buttons with download icons', () => {
      const { container } = render(<ExportButtons incidents={mockIncidents} />)

      const svgs = container.querySelectorAll('svg')
      expect(svgs).toHaveLength(2)
    })

    it('has correct aria-labels for accessibility', () => {
      render(<ExportButtons incidents={mockIncidents} />)

      expect(screen.getByLabelText('Export incidents to CSV')).toBeInTheDocument()
      expect(screen.getByLabelText('Export incidents to JSON')).toBeInTheDocument()
    })

    it('has correct title attributes for tooltips', () => {
      render(<ExportButtons incidents={mockIncidents} />)

      expect(screen.getByTitle('Export incidents to CSV')).toBeInTheDocument()
      expect(screen.getByTitle('Export incidents to JSON')).toBeInTheDocument()
    })

    it('renders buttons inside a container div', () => {
      const { container } = render(<ExportButtons incidents={mockIncidents} />)

      const wrapper = container.firstChild as HTMLElement
      expect(wrapper).toHaveClass('flex')
      expect(wrapper).toHaveClass('items-center')
      expect(wrapper).toHaveClass('gap-2')
    })
  })

  describe('Disabled State', () => {
    it('disables both buttons when isDisabled is true', () => {
      render(<ExportButtons incidents={mockIncidents} isDisabled={true} />)

      const csvButton = screen.getByText('Export CSV').closest('button')
      const jsonButton = screen.getByText('Export JSON').closest('button')

      expect(csvButton).toBeDisabled()
      expect(jsonButton).toBeDisabled()
    })

    it('enables buttons when isDisabled is false', () => {
      render(<ExportButtons incidents={mockIncidents} isDisabled={false} />)

      const csvButton = screen.getByText('Export CSV').closest('button')
      const jsonButton = screen.getByText('Export JSON').closest('button')

      expect(csvButton).not.toBeDisabled()
      expect(jsonButton).not.toBeDisabled()
    })

    it('enables buttons by default when isDisabled is not provided', () => {
      render(<ExportButtons incidents={mockIncidents} />)

      const csvButton = screen.getByText('Export CSV').closest('button')
      const jsonButton = screen.getByText('Export JSON').closest('button')

      expect(csvButton).not.toBeDisabled()
      expect(jsonButton).not.toBeDisabled()
    })

    it('applies disabled styling when isDisabled is true', () => {
      render(<ExportButtons incidents={mockIncidents} isDisabled={true} />)

      const csvButton = screen.getByText('Export CSV').closest('button')
      const jsonButton = screen.getByText('Export JSON').closest('button')

      expect(csvButton).toHaveClass('cursor-not-allowed')
      expect(csvButton).toHaveClass('opacity-50')
      expect(jsonButton).toHaveClass('cursor-not-allowed')
      expect(jsonButton).toHaveClass('opacity-50')
    })

    it('applies enabled styling when isDisabled is false', () => {
      render(<ExportButtons incidents={mockIncidents} isDisabled={false} />)

      const csvButton = screen.getByText('Export CSV').closest('button')
      const jsonButton = screen.getByText('Export JSON').closest('button')

      expect(csvButton).not.toHaveClass('cursor-not-allowed')
      expect(csvButton).not.toHaveClass('opacity-50')
      expect(jsonButton).not.toHaveClass('cursor-not-allowed')
      expect(jsonButton).not.toHaveClass('opacity-50')
    })
  })

  describe('CSV Export', () => {
    it('triggers CSV export when CSV button is clicked', () => {
      render(<ExportButtons incidents={mockIncidents} />)

      const csvButton = screen.getByText('Export CSV')
      fireEvent.click(csvButton)

      expect(formatIncidentsToCSV).toHaveBeenCalledWith(mockIncidents)
      expect(generateExportFilename).toHaveBeenCalledWith('csv')
      expect(downloadFile).toHaveBeenCalledWith(
        'mock-csv-content',
        'dronewatch-incidents-2025-06-15.csv',
        'text/csv'
      )
    })

    it('does not trigger CSV export when button is disabled', () => {
      render(<ExportButtons incidents={mockIncidents} isDisabled={true} />)

      const csvButton = screen.getByText('Export CSV')
      fireEvent.click(csvButton)

      expect(formatIncidentsToCSV).not.toHaveBeenCalled()
      expect(downloadFile).not.toHaveBeenCalled()
    })

    it('does not trigger CSV export when incidents array is empty', () => {
      render(<ExportButtons incidents={[]} />)

      const csvButton = screen.getByText('Export CSV')
      fireEvent.click(csvButton)

      expect(formatIncidentsToCSV).not.toHaveBeenCalled()
      expect(downloadFile).not.toHaveBeenCalled()
    })
  })

  describe('JSON Export', () => {
    it('triggers JSON export when JSON button is clicked', () => {
      render(<ExportButtons incidents={mockIncidents} />)

      const jsonButton = screen.getByText('Export JSON')
      fireEvent.click(jsonButton)

      expect(formatIncidentsToJSON).toHaveBeenCalledWith(mockIncidents)
      expect(generateExportFilename).toHaveBeenCalledWith('json')
      expect(downloadFile).toHaveBeenCalledWith(
        '{"mock": "json"}',
        'dronewatch-incidents-2025-06-15.json',
        'application/json'
      )
    })

    it('does not trigger JSON export when button is disabled', () => {
      render(<ExportButtons incidents={mockIncidents} isDisabled={true} />)

      const jsonButton = screen.getByText('Export JSON')
      fireEvent.click(jsonButton)

      expect(formatIncidentsToJSON).not.toHaveBeenCalled()
      expect(downloadFile).not.toHaveBeenCalled()
    })

    it('does not trigger JSON export when incidents array is empty', () => {
      render(<ExportButtons incidents={[]} />)

      const jsonButton = screen.getByText('Export JSON')
      fireEvent.click(jsonButton)

      expect(formatIncidentsToJSON).not.toHaveBeenCalled()
      expect(downloadFile).not.toHaveBeenCalled()
    })
  })

  describe('Edge Cases', () => {
    it('handles single incident correctly', () => {
      const singleIncident = [createMockIncident({ id: '1', title: 'Single Incident' })]
      render(<ExportButtons incidents={singleIncident} />)

      const csvButton = screen.getByText('Export CSV')
      fireEvent.click(csvButton)

      expect(formatIncidentsToCSV).toHaveBeenCalledWith(singleIncident)
    })

    it('handles many incidents correctly', () => {
      const manyIncidents = Array.from({ length: 100 }, (_, i) =>
        createMockIncident({ id: String(i), title: `Incident ${i}` })
      )
      render(<ExportButtons incidents={manyIncidents} />)

      const csvButton = screen.getByText('Export CSV')
      fireEvent.click(csvButton)

      expect(formatIncidentsToCSV).toHaveBeenCalledWith(manyIncidents)
    })

    it('clears mock state between exports', () => {
      render(<ExportButtons incidents={mockIncidents} />)

      const csvButton = screen.getByText('Export CSV')
      const jsonButton = screen.getByText('Export JSON')

      fireEvent.click(csvButton)
      fireEvent.click(jsonButton)

      expect(formatIncidentsToCSV).toHaveBeenCalledTimes(1)
      expect(formatIncidentsToJSON).toHaveBeenCalledTimes(1)
      expect(downloadFile).toHaveBeenCalledTimes(2)
    })

    it('both buttons can be clicked independently', () => {
      render(<ExportButtons incidents={mockIncidents} />)

      const csvButton = screen.getByText('Export CSV')
      const jsonButton = screen.getByText('Export JSON')

      // Click CSV first
      fireEvent.click(csvButton)
      expect(formatIncidentsToCSV).toHaveBeenCalledTimes(1)
      expect(formatIncidentsToJSON).not.toHaveBeenCalled()

      // Click JSON second
      fireEvent.click(jsonButton)
      expect(formatIncidentsToJSON).toHaveBeenCalledTimes(1)
    })
  })
})
