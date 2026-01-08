import { render, screen, fireEvent } from '@testing-library/react'
import { EvidenceLegendModal, useEvidenceLegendModal } from '../EvidenceLegendModal'
import { EVIDENCE_SYSTEM } from '@/constants/evidence'
import { renderHook, act } from '@testing-library/react'

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, className, ...props }: any) => (
      <div className={className} {...props}>
        {children}
      </div>
    ),
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}))

describe('EvidenceLegendModal', () => {
  const mockOnClose = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders when isOpen is true', () => {
    render(<EvidenceLegendModal isOpen={true} onClose={mockOnClose} />)

    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(screen.getByText('Evidence Levels')).toBeInTheDocument()
  })

  it('does not render when isOpen is false', () => {
    render(<EvidenceLegendModal isOpen={false} onClose={mockOnClose} />)

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(screen.queryByText('Evidence Levels')).not.toBeInTheDocument()
  })

  it('displays all 4 evidence levels', () => {
    render(<EvidenceLegendModal isOpen={true} onClose={mockOnClose} />)

    // Check that all 4 evidence levels are displayed with labels
    expect(screen.getByText(EVIDENCE_SYSTEM[4].label)).toBeInTheDocument()
    expect(screen.getByText(EVIDENCE_SYSTEM[3].label)).toBeInTheDocument()
    expect(screen.getByText(EVIDENCE_SYSTEM[2].label)).toBeInTheDocument()
    expect(screen.getByText(EVIDENCE_SYSTEM[1].label)).toBeInTheDocument()
  })

  it('displays descriptions for all evidence levels', () => {
    render(<EvidenceLegendModal isOpen={true} onClose={mockOnClose} />)

    expect(screen.getByText(EVIDENCE_SYSTEM[4].description)).toBeInTheDocument()
    expect(screen.getByText(EVIDENCE_SYSTEM[3].description)).toBeInTheDocument()
    expect(screen.getByText(EVIDENCE_SYSTEM[2].description)).toBeInTheDocument()
    expect(screen.getByText(EVIDENCE_SYSTEM[1].description)).toBeInTheDocument()
  })

  it('triggers onClose when close button is clicked', () => {
    render(<EvidenceLegendModal isOpen={true} onClose={mockOnClose} />)

    const closeButton = screen.getByLabelText('Close evidence legend')
    fireEvent.click(closeButton)

    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it('has correct ARIA attributes for accessibility', () => {
    render(<EvidenceLegendModal isOpen={true} onClose={mockOnClose} />)

    const dialog = screen.getByRole('dialog')
    expect(dialog).toHaveAttribute('aria-modal', 'true')
    expect(dialog).toHaveAttribute('aria-labelledby', 'evidence-legend-title')
  })

  it('displays the evidence levels list with correct role', () => {
    render(<EvidenceLegendModal isOpen={true} onClose={mockOnClose} />)

    const list = screen.getByRole('list', { name: 'Evidence scoring levels' })
    expect(list).toBeInTheDocument()

    const listItems = screen.getAllByRole('listitem')
    expect(listItems).toHaveLength(4)
  })

  it('displays subtitle text', () => {
    render(<EvidenceLegendModal isOpen={true} onClose={mockOnClose} />)

    expect(screen.getByText('How we verify drone incidents')).toBeInTheDocument()
  })

  it('displays footer text', () => {
    render(<EvidenceLegendModal isOpen={true} onClose={mockOnClose} />)

    expect(
      screen.getByText('Higher scores indicate more reliable evidence sources')
    ).toBeInTheDocument()
  })

  it('closes on Escape key press', () => {
    render(<EvidenceLegendModal isOpen={true} onClose={mockOnClose} />)

    fireEvent.keyDown(document, { key: 'Escape' })

    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it('closes on click outside modal', () => {
    render(<EvidenceLegendModal isOpen={true} onClose={mockOnClose} />)

    // The backdrop is the outer div with role="dialog"
    const backdrop = screen.getByRole('dialog')
    fireEvent.mouseDown(backdrop)

    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })
})

describe('useEvidenceLegendModal hook', () => {
  it('initializes with modal closed', () => {
    const { result } = renderHook(() => useEvidenceLegendModal())

    expect(result.current.isOpen).toBe(false)
  })

  it('opens modal when openModal is called', () => {
    const { result } = renderHook(() => useEvidenceLegendModal())

    act(() => {
      result.current.openModal()
    })

    expect(result.current.isOpen).toBe(true)
  })

  it('closes modal when closeModal is called', () => {
    const { result } = renderHook(() => useEvidenceLegendModal())

    act(() => {
      result.current.openModal()
    })
    expect(result.current.isOpen).toBe(true)

    act(() => {
      result.current.closeModal()
    })
    expect(result.current.isOpen).toBe(false)
  })
})
