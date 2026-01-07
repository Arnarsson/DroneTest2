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
jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}))

describe('FilterPanel', () => {
  const mockFilters: FilterState = {
    searchQuery: '',
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
      searchQuery: '',
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
      searchQuery: 'test query',
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
      searchQuery: '',
      minEvidence: 1,
      country: 'all',
      status: 'all',
      assetType: null,
      dateRange: 'all',
    })
  })

  it('shows active filter count badge', () => {
    const activeFilters: FilterState = {
      searchQuery: '',
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
      searchQuery: '',
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

  // Search Input Tests
  it('renders search input with placeholder', () => {
    render(
      <FilterPanel
        filters={mockFilters}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={true}
        onToggle={mockOnToggle}
      />
    )

    const searchInput = screen.getByPlaceholderText('Search incidents...')
    expect(searchInput).toBeInTheDocument()
    expect(searchInput).toHaveAttribute('type', 'text')
  })

  it('calls onChange with searchQuery when search input changes', () => {
    render(
      <FilterPanel
        filters={mockFilters}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={true}
        onToggle={mockOnToggle}
      />
    )

    const searchInput = screen.getByPlaceholderText('Search incidents...')
    fireEvent.change(searchInput, { target: { value: 'airport' } })

    expect(mockOnChange).toHaveBeenCalledWith({
      ...mockFilters,
      searchQuery: 'airport',
    })
  })

  it('displays current search query value', () => {
    const filtersWithSearch: FilterState = {
      ...mockFilters,
      searchQuery: 'test search',
    }

    render(
      <FilterPanel
        filters={filtersWithSearch}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={true}
        onToggle={mockOnToggle}
      />
    )

    const searchInput = screen.getByPlaceholderText('Search incidents...')
    expect(searchInput).toHaveValue('test search')
  })

  it('clears searchQuery when Clear all is clicked', () => {
    const filtersWithSearch: FilterState = {
      searchQuery: 'airport drone',
      minEvidence: 1,
      country: 'all',
      status: 'all',
      dateRange: 'all',
      assetType: null,
    }

    render(
      <FilterPanel
        filters={filtersWithSearch}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={true}
        onToggle={mockOnToggle}
      />
    )

    const clearButton = screen.getByText('Clear all')
    fireEvent.click(clearButton)

    expect(mockOnChange).toHaveBeenCalledWith({
      searchQuery: '',
      minEvidence: 1,
      country: 'all',
      status: 'all',
      assetType: null,
      dateRange: 'all',
    })
  })

  it('includes searchQuery in active filter count when non-empty', () => {
    const filtersWithSearch: FilterState = {
      searchQuery: 'test',
      minEvidence: 1,
      country: 'all',
      status: 'all',
      dateRange: 'all',
      assetType: null,
    }

    render(
      <FilterPanel
        filters={filtersWithSearch}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={true}
        onToggle={mockOnToggle}
      />
    )

    expect(screen.getByText('1 active filter')).toBeInTheDocument()
  })

  it('does not include empty searchQuery in active filter count', () => {
    render(
      <FilterPanel
        filters={mockFilters}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={true}
        onToggle={mockOnToggle}
      />
    )

    // With mockFilters having all defaults, there should be no active filters
    expect(screen.queryByText(/active filter/)).not.toBeInTheDocument()
  })

  it('does not include whitespace-only searchQuery in active filter count', () => {
    const filtersWithWhitespace: FilterState = {
      searchQuery: '   ',
      minEvidence: 1,
      country: 'all',
      status: 'all',
      dateRange: 'all',
      assetType: null,
    }

    render(
      <FilterPanel
        filters={filtersWithWhitespace}
        onChange={mockOnChange}
        incidentCount={10}
        isOpen={true}
        onToggle={mockOnToggle}
      />
    )

    // Whitespace-only searchQuery should not count as active filter
    expect(screen.queryByText(/active filter/)).not.toBeInTheDocument()
  })
})
