import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { FilterPanel } from '../FilterPanel'
import type { FilterState } from '@/types'
import { logger } from '@/lib/logger'

// Mock logger
jest.mock('@/lib/logger', () => ({
  logger: {
    debug: jest.fn(),
    info: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
  },
}))

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

// Mock sonner toast
const mockToast = {
  success: jest.fn(),
  error: jest.fn(),
}
jest.mock('sonner', () => ({
  toast: mockToast,
}))

describe('FilterPanel', () => {
  const mockFilters: FilterState = {
    minEvidence: 1,
    country: 'all',
    status: 'all',
    dateRange: 'all',
    assetType: null,
  }

  const mockOnChange = jest.fn()
  const mockOnToggle = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders all filter controls', () => {
    render(
      <FilterPanel
        filters={mockFilters}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={true}
        onToggle={mockOnToggle}
      />
    )

    expect(screen.getByText('Filters')).toBeInTheDocument()
    expect(screen.getByText('Evidence Level')).toBeInTheDocument()
    expect(screen.getByText('Location')).toBeInTheDocument()
    expect(screen.getByText('Time Period')).toBeInTheDocument()
  })

  it('displays incident count correctly', () => {
    render(
      <FilterPanel
        filters={mockFilters}
        onChange={mockOnChange}
        incidentCount={5}
        isOpen={true}
        onToggle={mockOnToggle}
      />
    )

    expect(screen.getByText('5 incidents found')).toBeInTheDocument()
  })

  it('displays singular "incident" when count is 1', () => {
    render(
      <FilterPanel
        filters={mockFilters}
        onChange={mockOnChange}
        incidentCount={1}
        isOpen={true}
        onToggle={mockOnToggle}
      />
    )

    expect(screen.getByText('1 incident found')).toBeInTheDocument()
  })

  it('calls onChange when evidence slider changes', () => {
    render(
      <FilterPanel
        filters={mockFilters}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={true}
        onToggle={mockOnToggle}
      />
    )

    const button = screen.getByText('3+ Verified')
    fireEvent.click(button)

    expect(mockOnChange).toHaveBeenCalledWith({
      ...mockFilters,
      minEvidence: 3,
    })
  })

  it('calls onChange when country dropdown changes', () => {
    render(
      <FilterPanel
        filters={mockFilters}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={true}
        onToggle={mockOnToggle}
      />
    )

    const select = screen.getByDisplayValue('All Countries')
    fireEvent.change(select, { target: { value: 'DK' } })

    expect(mockOnChange).toHaveBeenCalledWith({
      ...mockFilters,
      country: 'DK',
    })
  })

  it('displays all country options', () => {
    render(
      <FilterPanel
        filters={mockFilters}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={true}
        onToggle={mockOnToggle}
      />
    )

    expect(screen.getByText('All Countries')).toBeInTheDocument()
    expect(screen.getByText('🇩🇰 Denmark')).toBeInTheDocument()
    expect(screen.getByText('🇳🇴 Norway')).toBeInTheDocument()
    expect(screen.getByText('🇸🇪 Sweden')).toBeInTheDocument()
    expect(screen.getByText('🇫🇮 Finland')).toBeInTheDocument()
    expect(screen.getByText('🇵🇱 Poland')).toBeInTheDocument()
    expect(screen.getByText('🇳🇱 Netherlands')).toBeInTheDocument()
  })

  it('calls onChange when status filter changes', () => {
    render(
      <FilterPanel
        filters={mockFilters}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={true}
        onToggle={mockOnToggle}
      />
    )

    const select = screen.getByDisplayValue('All Status')
    fireEvent.change(select, { target: { value: 'active' } })

    expect(mockOnChange).toHaveBeenCalledWith({
      ...mockFilters,
      status: 'active',
    })
  })

  it('displays all status options', () => {
    render(
      <FilterPanel
        filters={mockFilters}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={true}
        onToggle={mockOnToggle}
      />
    )

    expect(screen.getByText('All Status')).toBeInTheDocument()
    expect(screen.getByText('Active')).toBeInTheDocument()
    expect(screen.getByText('Resolved')).toBeInTheDocument()
    expect(screen.getByText('Unconfirmed')).toBeInTheDocument()
  })

  it('persists filter state values', () => {
    const activeFilters: FilterState = {
      minEvidence: 3,
      country: 'DK',
      status: 'active',
      dateRange: 'week',
      assetType: 'airport',
    }

    render(
      <FilterPanel
        filters={activeFilters}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={true}
        onToggle={mockOnToggle}
      />
    )

    expect(screen.getByDisplayValue('🇩🇰 Denmark')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Active')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Last 7 Days')).toBeInTheDocument()
    expect(screen.getByDisplayValue('✈️ Airport')).toBeInTheDocument()
  })

  it('calls logger debug on render', () => {
    render(
      <FilterPanel
        filters={mockFilters}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={true}
        onToggle={mockOnToggle}
      />
    )

    expect(logger.debug).toHaveBeenCalledWith('[FilterPanel] Rendered')
    expect(logger.debug).toHaveBeenCalledWith('[FilterPanel] incidentCount:', 10)
    expect(logger.debug).toHaveBeenCalledWith('[FilterPanel] filters:', mockFilters)
  })

  it('resets all filters when Clear all is clicked', () => {
    const activeFilters: FilterState = {
      minEvidence: 3,
      country: 'DK',
      status: 'active',
      dateRange: 'week',
      assetType: 'airport',
    }

    render(
      <FilterPanel
        filters={activeFilters}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={true}
        onToggle={mockOnToggle}
      />
    )

    const clearButton = screen.getByText('Clear all')
    fireEvent.click(clearButton)

    expect(mockOnChange).toHaveBeenCalledWith({
      minEvidence: 1,
      country: 'all',
      status: 'all',
      assetType: null,
      dateRange: 'all',
    })
  })

  it('shows toast notification when filters are cleared', () => {
    const activeFilters: FilterState = {
      minEvidence: 3,
      country: 'DK',
      status: 'active',
      dateRange: 'week',
      assetType: 'airport',
    }

    render(
      <FilterPanel
        filters={activeFilters}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={true}
        onToggle={mockOnToggle}
      />
    )

    const clearButton = screen.getByText('Clear all')
    fireEvent.click(clearButton)

    expect(mockToast.success).toHaveBeenCalledWith('Filters cleared')
  })

  it('shows active filter count badge', () => {
    const activeFilters: FilterState = {
      minEvidence: 3,
      country: 'DK',
      status: 'active',
      dateRange: 'week',
      assetType: 'airport',
    }

    render(
      <FilterPanel
        filters={activeFilters}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={true}
        onToggle={mockOnToggle}
      />
    )

    expect(screen.getByText('5 active filters')).toBeInTheDocument()
  })

  it('displays quick filter chips', () => {
    render(
      <FilterPanel
        filters={mockFilters}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={true}
        onToggle={mockOnToggle}
      />
    )

    expect(screen.getByText('Airports')).toBeInTheDocument()
    expect(screen.getByText('Military')).toBeInTheDocument()
    expect(screen.getByText('Today')).toBeInTheDocument()
    expect(screen.getByText('Verified')).toBeInTheDocument()
  })

  it('toggles airport quick filter', () => {
    render(
      <FilterPanel
        filters={mockFilters}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={true}
        onToggle={mockOnToggle}
      />
    )

    const airportChip = screen.getByText('Airports')
    fireEvent.click(airportChip)

    expect(mockOnChange).toHaveBeenCalledWith({
      ...mockFilters,
      assetType: 'airport',
    })
  })

  it('has correct ARIA labels for accessibility', () => {
    render(
      <FilterPanel
        filters={mockFilters}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={false}
        onToggle={mockOnToggle}
      />
    )

    const mobileButton = screen.getByLabelText('Open filters')
    expect(mobileButton).toBeInTheDocument()
    expect(mobileButton).toHaveAttribute('aria-expanded', 'false')
  })

  it('updates ARIA label when filters are active', () => {
    const activeFilters: FilterState = {
      ...mockFilters,
      minEvidence: 3,
      country: 'DK',
    }

    render(
      <FilterPanel
        filters={activeFilters}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={false}
        onToggle={mockOnToggle}
      />
    )

    const mobileButton = screen.getByLabelText('Open filters (2 active)')
    expect(mobileButton).toBeInTheDocument()
  })

  it('calls onToggle when mobile button is clicked', () => {
    render(
      <FilterPanel
        filters={mockFilters}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={false}
        onToggle={mockOnToggle}
      />
    )

    const mobileButton = screen.getByLabelText('Open filters')
    fireEvent.click(mobileButton)

    expect(mockOnToggle).toHaveBeenCalled()
  })

  it('displays all asset type options', () => {
    render(
      <FilterPanel
        filters={mockFilters}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={true}
        onToggle={mockOnToggle}
      />
    )

    expect(screen.getByText('All Types')).toBeInTheDocument()
    expect(screen.getByText('✈️ Airport')).toBeInTheDocument()
    expect(screen.getByText('⚓ Harbor')).toBeInTheDocument()
    expect(screen.getByText('🛡️ Military')).toBeInTheDocument()
    expect(screen.getByText('⚡ Power Plant')).toBeInTheDocument()
    expect(screen.getByText('📍 Other')).toBeInTheDocument()
  })

  it('displays all time period options', () => {
    render(
      <FilterPanel
        filters={mockFilters}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={true}
        onToggle={mockOnToggle}
      />
    )

    expect(screen.getByText('All Time')).toBeInTheDocument()
    expect(screen.getByText('Last 24 Hours')).toBeInTheDocument()
    expect(screen.getByText('Last 7 Days')).toBeInTheDocument()
    expect(screen.getByText('Last 30 Days')).toBeInTheDocument()
  })

  describe('Keyboard Hints', () => {
    it('displays keyboard hints on quick filter chips', () => {
      render(
        <FilterPanel
          filters={mockFilters}
          onChange={mockOnChange}
          incidentCount={10}
          isOpen={true}
          onToggle={mockOnToggle}
        />
      )

      // Check that all quick filter keyboard hints are displayed
      expect(screen.getByText('A')).toBeInTheDocument()
      expect(screen.getByText('M')).toBeInTheDocument()
      expect(screen.getByText('T')).toBeInTheDocument()
      expect(screen.getByText('V')).toBeInTheDocument()
    })

    it('displays keyboard hint F next to Filters header', () => {
      render(
        <FilterPanel
          filters={mockFilters}
          onChange={mockOnChange}
          incidentCount={10}
          isOpen={true}
          onToggle={mockOnToggle}
        />
      )

      // The F hint should be visible in the header
      expect(screen.getByText('F')).toBeInTheDocument()
    })

    it('displays keyboard hint R on reset button when filters are active', () => {
      const activeFilters: FilterState = {
        minEvidence: 3,
        country: 'DK',
        status: 'all',
        dateRange: 'all',
        assetType: null,
      }

      render(
        <FilterPanel
          filters={activeFilters}
          onChange={mockOnChange}
          incidentCount={10}
          isOpen={true}
          onToggle={mockOnToggle}
        />
      )

      // The R hint should be visible next to Clear all
      expect(screen.getByText('R')).toBeInTheDocument()
    })

    it('keyboard hints have aria-hidden attribute for accessibility', () => {
      const activeFilters: FilterState = {
        minEvidence: 3,
        country: 'all',
        status: 'all',
        dateRange: 'all',
        assetType: null,
      }

      render(
        <FilterPanel
          filters={activeFilters}
          onChange={mockOnChange}
          incidentCount={10}
          isOpen={true}
          onToggle={mockOnToggle}
        />
      )

      // All keyboard hint badges should be hidden from screen readers
      const keyboardHints = ['A', 'M', 'T', 'V', 'F', 'R']
      keyboardHints.forEach((hint) => {
        const hintElement = screen.getByText(hint)
        expect(hintElement).toHaveAttribute('aria-hidden', 'true')
      })
    })

    it('quick filter chips have title attribute with shortcut hint', () => {
      render(
        <FilterPanel
          filters={mockFilters}
          onChange={mockOnChange}
          incidentCount={10}
          isOpen={true}
          onToggle={mockOnToggle}
        />
      )

      // Check that quick filter buttons have title attributes
      expect(screen.getByTitle('Press A to toggle')).toBeInTheDocument()
      expect(screen.getByTitle('Press M to toggle')).toBeInTheDocument()
      expect(screen.getByTitle('Press T to toggle')).toBeInTheDocument()
      expect(screen.getByTitle('Press V to toggle')).toBeInTheDocument()
    })

    it('filter toggle header hint has title attribute', () => {
      render(
        <FilterPanel
          filters={mockFilters}
          onChange={mockOnChange}
          incidentCount={10}
          isOpen={true}
          onToggle={mockOnToggle}
        />
      )

      // The F hint in the header should have a descriptive title
      expect(screen.getByTitle('Press F to toggle filters')).toBeInTheDocument()
    })

    it('mobile filter toggle button includes keyboard hint in aria-label', () => {
      render(
        <FilterPanel
          filters={mockFilters}
          onChange={mockOnChange}
          incidentCount={10}
          isOpen={false}
          onToggle={mockOnToggle}
        />
      )

      // Mobile button should mention keyboard shortcut in aria-label
      const mobileButton = screen.getByLabelText('Open filters (Press F)')
      expect(mobileButton).toBeInTheDocument()
    })

    it('mobile filter toggle button with active filters includes keyboard hint', () => {
      const activeFilters: FilterState = {
        minEvidence: 3,
        country: 'DK',
        status: 'all',
        dateRange: 'all',
        assetType: null,
      }

      render(
        <FilterPanel
          filters={activeFilters}
          onChange={mockOnChange}
          incidentCount={10}
          isOpen={false}
          onToggle={mockOnToggle}
        />
      )

      // Mobile button with active filters should include keyboard shortcut
      const mobileButton = screen.getByLabelText('Open filters (2 active) (Press F)')
      expect(mobileButton).toBeInTheDocument()
    })
  })
})
