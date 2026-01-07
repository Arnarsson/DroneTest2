import { renderHook, act } from '@testing-library/react'
import { useURLFilterState } from '../useURLFilterState'
import { DEFAULT_FILTER_STATE } from '@/lib/urlFilterParams'
import type { FilterState } from '@/types'

// Mock Next.js navigation hooks
const mockReplace = jest.fn()
const mockGet = jest.fn()

// Store mock searchParams to simulate URL changes
let mockSearchParams: { get: jest.Mock }

jest.mock('next/navigation', () => ({
  useSearchParams: () => mockSearchParams,
  useRouter: () => ({
    replace: mockReplace,
  }),
  usePathname: () => '/',
}))

// Mock window.location.search for popstate tests
const originalLocation = window.location
let mockLocationSearch = ''

beforeAll(() => {
  delete (window as any).location
  window.location = {
    ...originalLocation,
    get search() {
      return mockLocationSearch
    },
  } as Location
})

afterAll(() => {
  window.location = originalLocation
})

describe('useURLFilterState', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    // Default to returning null for all params (uses defaults)
    mockGet.mockReturnValue(null)
    // Initialize mock searchParams
    mockSearchParams = { get: mockGet }
    // Reset mock location search
    mockLocationSearch = ''
  })

  describe('initial state from URL', () => {
    it('returns default filter state when no URL params present', () => {
      mockGet.mockReturnValue(null)

      const { result } = renderHook(() => useURLFilterState())

      expect(result.current.filters).toEqual(DEFAULT_FILTER_STATE)
    })

    it('reads minEvidence from URL', () => {
      mockGet.mockImplementation((key: string) => {
        if (key === 'min_evidence') return '3'
        return null
      })

      const { result } = renderHook(() => useURLFilterState())

      expect(result.current.filters.minEvidence).toBe(3)
    })

    it('reads country from URL', () => {
      mockGet.mockImplementation((key: string) => {
        if (key === 'country') return 'DK'
        return null
      })

      const { result } = renderHook(() => useURLFilterState())

      expect(result.current.filters.country).toBe('DK')
    })

    it('reads status from URL', () => {
      mockGet.mockImplementation((key: string) => {
        if (key === 'status') return 'active'
        return null
      })

      const { result } = renderHook(() => useURLFilterState())

      expect(result.current.filters.status).toBe('active')
    })

    it('reads assetType from URL', () => {
      mockGet.mockImplementation((key: string) => {
        if (key === 'asset_type') return 'airport'
        return null
      })

      const { result } = renderHook(() => useURLFilterState())

      expect(result.current.filters.assetType).toBe('airport')
    })

    it('reads dateRange from URL', () => {
      mockGet.mockImplementation((key: string) => {
        if (key === 'date_range') return 'week'
        return null
      })

      const { result } = renderHook(() => useURLFilterState())

      expect(result.current.filters.dateRange).toBe('week')
    })

    it('reads all filter values from URL', () => {
      mockGet.mockImplementation((key: string) => {
        const values: Record<string, string> = {
          min_evidence: '3',
          country: 'DK',
          status: 'active',
          asset_type: 'airport',
          date_range: 'week',
        }
        return values[key] || null
      })

      const { result } = renderHook(() => useURLFilterState())

      expect(result.current.filters).toEqual({
        minEvidence: 3,
        country: 'DK',
        status: 'active',
        assetType: 'airport',
        dateRange: 'week',
      })
    })

    it('uses defaults for invalid minEvidence values', () => {
      mockGet.mockImplementation((key: string) => {
        if (key === 'min_evidence') return 'invalid'
        return null
      })

      const { result } = renderHook(() => useURLFilterState())

      expect(result.current.filters.minEvidence).toBe(
        DEFAULT_FILTER_STATE.minEvidence
      )
    })

    it('uses defaults for out-of-range minEvidence values', () => {
      mockGet.mockImplementation((key: string) => {
        if (key === 'min_evidence') return '10'
        return null
      })

      const { result } = renderHook(() => useURLFilterState())

      expect(result.current.filters.minEvidence).toBe(
        DEFAULT_FILTER_STATE.minEvidence
      )
    })

    it('uses defaults for invalid dateRange values', () => {
      mockGet.mockImplementation((key: string) => {
        if (key === 'date_range') return 'year'
        return null
      })

      const { result } = renderHook(() => useURLFilterState())

      expect(result.current.filters.dateRange).toBe(
        DEFAULT_FILTER_STATE.dateRange
      )
    })
  })

  describe('setFilters updates URL', () => {
    it('updates URL when filters change', () => {
      const { result } = renderHook(() => useURLFilterState())

      const newFilters: FilterState = {
        minEvidence: 3,
        country: 'DK',
        status: 'active',
        assetType: 'airport',
        dateRange: 'week',
      }

      act(() => {
        result.current.setFilters(newFilters)
      })

      expect(mockReplace).toHaveBeenCalledTimes(1)
      expect(mockReplace).toHaveBeenCalledWith(
        expect.stringContaining('min_evidence=3'),
        expect.objectContaining({ scroll: false })
      )
      expect(mockReplace).toHaveBeenCalledWith(
        expect.stringContaining('country=DK'),
        expect.objectContaining({ scroll: false })
      )
      expect(mockReplace).toHaveBeenCalledWith(
        expect.stringContaining('status=active'),
        expect.objectContaining({ scroll: false })
      )
      expect(mockReplace).toHaveBeenCalledWith(
        expect.stringContaining('asset_type=airport'),
        expect.objectContaining({ scroll: false })
      )
      expect(mockReplace).toHaveBeenCalledWith(
        expect.stringContaining('date_range=week'),
        expect.objectContaining({ scroll: false })
      )
    })

    it('uses router.replace to avoid history cluttering', () => {
      const { result } = renderHook(() => useURLFilterState())

      const newFilters: FilterState = {
        minEvidence: 2,
        country: 'SE',
        status: 'all',
        assetType: null,
        dateRange: 'month',
      }

      act(() => {
        result.current.setFilters(newFilters)
      })

      // Verify replace was called, not push
      expect(mockReplace).toHaveBeenCalled()
    })

    it('passes scroll: false to prevent page scroll', () => {
      const { result } = renderHook(() => useURLFilterState())

      act(() => {
        result.current.setFilters({
          ...DEFAULT_FILTER_STATE,
          country: 'NO',
        })
      })

      expect(mockReplace).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({ scroll: false })
      )
    })

    it('omits default values from URL params', () => {
      const { result } = renderHook(() => useURLFilterState())

      // Set a single non-default value
      act(() => {
        result.current.setFilters({
          ...DEFAULT_FILTER_STATE,
          country: 'DK',
        })
      })

      const urlArg = mockReplace.mock.calls[0][0]

      // Should include country
      expect(urlArg).toContain('country=DK')

      // Should NOT include default values
      expect(urlArg).not.toContain('min_evidence=')
      expect(urlArg).not.toContain('status=')
      expect(urlArg).not.toContain('asset_type=')
      expect(urlArg).not.toContain('date_range=')
    })

    it('sets clean URL without query string when all defaults', () => {
      const { result } = renderHook(() => useURLFilterState())

      act(() => {
        result.current.setFilters(DEFAULT_FILTER_STATE)
      })

      expect(mockReplace).toHaveBeenCalledWith('/', expect.any(Object))
    })

    it('includes minEvidence in URL when non-default', () => {
      const { result } = renderHook(() => useURLFilterState())

      act(() => {
        result.current.setFilters({
          ...DEFAULT_FILTER_STATE,
          minEvidence: 3,
        })
      })

      const urlArg = mockReplace.mock.calls[0][0]
      expect(urlArg).toContain('min_evidence=3')
    })

    it('includes assetType in URL when set', () => {
      const { result } = renderHook(() => useURLFilterState())

      act(() => {
        result.current.setFilters({
          ...DEFAULT_FILTER_STATE,
          assetType: 'military',
        })
      })

      const urlArg = mockReplace.mock.calls[0][0]
      expect(urlArg).toContain('asset_type=military')
    })

    it('omits assetType from URL when null', () => {
      const { result } = renderHook(() => useURLFilterState())

      act(() => {
        result.current.setFilters({
          ...DEFAULT_FILTER_STATE,
          assetType: null,
        })
      })

      const urlArg = mockReplace.mock.calls[0][0]
      expect(urlArg).not.toContain('asset_type=')
    })
  })

  describe('return value structure', () => {
    it('returns filters and setFilters', () => {
      const { result } = renderHook(() => useURLFilterState())

      expect(result.current).toHaveProperty('filters')
      expect(result.current).toHaveProperty('setFilters')
    })

    it('filters is a FilterState object', () => {
      const { result } = renderHook(() => useURLFilterState())

      expect(result.current.filters).toHaveProperty('minEvidence')
      expect(result.current.filters).toHaveProperty('country')
      expect(result.current.filters).toHaveProperty('status')
      expect(result.current.filters).toHaveProperty('assetType')
      expect(result.current.filters).toHaveProperty('dateRange')
    })

    it('setFilters is a function', () => {
      const { result } = renderHook(() => useURLFilterState())

      expect(typeof result.current.setFilters).toBe('function')
    })
  })

  describe('URL param key mapping', () => {
    it('uses snake_case keys for URL parameters', () => {
      const { result } = renderHook(() => useURLFilterState())

      act(() => {
        result.current.setFilters({
          minEvidence: 2,
          country: 'DK',
          status: 'active',
          assetType: 'airport',
          dateRange: 'week',
        })
      })

      const urlArg = mockReplace.mock.calls[0][0]

      // Verify snake_case keys are used
      expect(urlArg).toContain('min_evidence=')
      expect(urlArg).toContain('date_range=')
      expect(urlArg).toContain('asset_type=')

      // Verify camelCase keys are NOT used
      expect(urlArg).not.toContain('minEvidence=')
      expect(urlArg).not.toContain('dateRange=')
      expect(urlArg).not.toContain('assetType=')
    })
  })

  describe('memoization', () => {
    it('setFilters reference is stable across renders', () => {
      const { result, rerender } = renderHook(() => useURLFilterState())

      const firstSetFilters = result.current.setFilters

      rerender()

      // setFilters should have the same reference due to useCallback
      expect(result.current.setFilters).toBe(firstSetFilters)
    })
  })

  describe('edge cases', () => {
    it('handles multiple consecutive filter updates', () => {
      const { result } = renderHook(() => useURLFilterState())

      act(() => {
        result.current.setFilters({
          ...DEFAULT_FILTER_STATE,
          country: 'DK',
        })
      })

      act(() => {
        result.current.setFilters({
          ...DEFAULT_FILTER_STATE,
          country: 'SE',
        })
      })

      expect(mockReplace).toHaveBeenCalledTimes(2)
      expect(mockReplace).toHaveBeenLastCalledWith(
        expect.stringContaining('country=SE'),
        expect.any(Object)
      )
    })

    it('handles boundary values for minEvidence', () => {
      mockGet.mockImplementation((key: string) => {
        if (key === 'min_evidence') return '4'
        return null
      })

      const { result } = renderHook(() => useURLFilterState())

      expect(result.current.filters.minEvidence).toBe(4)
    })

    it('handles mixed valid and invalid URL params', () => {
      mockGet.mockImplementation((key: string) => {
        const values: Record<string, string> = {
          min_evidence: 'invalid', // Invalid - should default
          country: 'DK', // Valid
          date_range: 'year', // Invalid - should default
          status: 'active', // Valid
        }
        return values[key] || null
      })

      const { result } = renderHook(() => useURLFilterState())

      expect(result.current.filters).toEqual({
        minEvidence: DEFAULT_FILTER_STATE.minEvidence, // Defaulted
        country: 'DK',
        status: 'active',
        assetType: null, // Default
        dateRange: DEFAULT_FILTER_STATE.dateRange, // Defaulted
      })
    })
  })

  describe('browser back/forward navigation', () => {
    it('updates filter state when popstate event fires', () => {
      const { result } = renderHook(() => useURLFilterState())

      // Verify initial state
      expect(result.current.filters).toEqual(DEFAULT_FILTER_STATE)

      // Simulate browser navigation to a URL with filter params
      mockLocationSearch = '?country=DK&min_evidence=3&date_range=week'

      // Dispatch popstate event (simulates browser back/forward)
      act(() => {
        window.dispatchEvent(new PopStateEvent('popstate'))
      })

      // Filter state should update to match URL
      expect(result.current.filters.country).toBe('DK')
      expect(result.current.filters.minEvidence).toBe(3)
      expect(result.current.filters.dateRange).toBe('week')
    })

    it('restores filters when navigating back to URL with params', () => {
      // Start with some filter params in URL
      mockGet.mockImplementation((key: string) => {
        const values: Record<string, string> = {
          country: 'SE',
          min_evidence: '2',
        }
        return values[key] || null
      })
      mockLocationSearch = '?country=SE&min_evidence=2'

      const { result } = renderHook(() => useURLFilterState())

      // Verify initial state from URL
      expect(result.current.filters.country).toBe('SE')
      expect(result.current.filters.minEvidence).toBe(2)

      // Simulate navigating to a page with different filters (via popstate)
      mockLocationSearch = '?country=NO&min_evidence=4&status=active'

      act(() => {
        window.dispatchEvent(new PopStateEvent('popstate'))
      })

      // Filter state should update
      expect(result.current.filters.country).toBe('NO')
      expect(result.current.filters.minEvidence).toBe(4)
      expect(result.current.filters.status).toBe('active')
    })

    it('restores default filters when navigating back to URL without params', () => {
      // Start with filter params in URL
      mockGet.mockImplementation((key: string) => {
        if (key === 'country') return 'DK'
        return null
      })
      mockLocationSearch = '?country=DK'

      const { result } = renderHook(() => useURLFilterState())

      expect(result.current.filters.country).toBe('DK')

      // Navigate back to URL without params
      mockLocationSearch = ''

      act(() => {
        window.dispatchEvent(new PopStateEvent('popstate'))
      })

      // Should restore to defaults
      expect(result.current.filters).toEqual(DEFAULT_FILTER_STATE)
    })

    it('cleans up popstate event listener on unmount', () => {
      const addEventListenerSpy = jest.spyOn(window, 'addEventListener')
      const removeEventListenerSpy = jest.spyOn(window, 'removeEventListener')

      const { unmount } = renderHook(() => useURLFilterState())

      // Verify event listener was added
      expect(addEventListenerSpy).toHaveBeenCalledWith(
        'popstate',
        expect.any(Function)
      )

      // Get the handler that was registered
      const handler = addEventListenerSpy.mock.calls.find(
        (call) => call[0] === 'popstate'
      )?.[1]

      unmount()

      // Verify event listener was removed with the same handler
      expect(removeEventListenerSpy).toHaveBeenCalledWith('popstate', handler)

      addEventListenerSpy.mockRestore()
      removeEventListenerSpy.mockRestore()
    })

    it('handles multiple consecutive popstate events correctly', () => {
      const { result } = renderHook(() => useURLFilterState())

      // First navigation
      mockLocationSearch = '?country=DK'
      act(() => {
        window.dispatchEvent(new PopStateEvent('popstate'))
      })
      expect(result.current.filters.country).toBe('DK')

      // Second navigation
      mockLocationSearch = '?country=SE&date_range=month'
      act(() => {
        window.dispatchEvent(new PopStateEvent('popstate'))
      })
      expect(result.current.filters.country).toBe('SE')
      expect(result.current.filters.dateRange).toBe('month')

      // Third navigation - back to defaults
      mockLocationSearch = ''
      act(() => {
        window.dispatchEvent(new PopStateEvent('popstate'))
      })
      expect(result.current.filters).toEqual(DEFAULT_FILTER_STATE)
    })

    it('does not call router.replace on popstate events', () => {
      const { result } = renderHook(() => useURLFilterState())

      mockLocationSearch = '?country=DK'
      act(() => {
        window.dispatchEvent(new PopStateEvent('popstate'))
      })

      // popstate should NOT trigger router.replace (would cause navigation loop)
      expect(mockReplace).not.toHaveBeenCalled()
      // But filters should still update
      expect(result.current.filters.country).toBe('DK')
    })
  })
})
