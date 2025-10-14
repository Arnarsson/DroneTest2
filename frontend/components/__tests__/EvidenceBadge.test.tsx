import { render, screen } from '@testing-library/react'
import { EvidenceBadge } from '../EvidenceBadge'
import { EVIDENCE_SYSTEM } from '@/constants/evidence'

describe('EvidenceBadge', () => {
  it('renders score 4 as OFFICIAL with green badge', () => {
    render(<EvidenceBadge score={4} />)

    const badge = screen.getByText('OFFICIAL')
    expect(badge).toBeInTheDocument()

    const container = badge.parentElement
    expect(container).toHaveClass('bg-emerald-500')
    expect(container).toHaveClass('text-white')
  })

  it('renders score 3 as VERIFIED with amber badge', () => {
    render(<EvidenceBadge score={3} />)

    const badge = screen.getByText('VERIFIED')
    expect(badge).toBeInTheDocument()

    const container = badge.parentElement
    expect(container).toHaveClass('bg-amber-500')
    expect(container).toHaveClass('text-white')
  })

  it('renders score 2 as REPORTED with orange badge', () => {
    render(<EvidenceBadge score={2} />)

    const badge = screen.getByText('REPORTED')
    expect(badge).toBeInTheDocument()

    const container = badge.parentElement
    expect(container).toHaveClass('bg-orange-500')
    expect(container).toHaveClass('text-white')
  })

  it('renders score 1 as UNCONFIRMED with red badge', () => {
    render(<EvidenceBadge score={1} />)

    const badge = screen.getByText('UNCONFIRMED')
    expect(badge).toBeInTheDocument()

    const container = badge.parentElement
    expect(container).toHaveClass('bg-red-500')
    expect(container).toHaveClass('text-white')
  })

  it('uses evidence constants from constants/evidence.ts', () => {
    render(<EvidenceBadge score={4} />)

    const badge = screen.getByText('OFFICIAL')
    expect(badge).toBeInTheDocument()

    // Verify we're using the same constants
    expect(EVIDENCE_SYSTEM[4].label).toBe('OFFICIAL')
    expect(EVIDENCE_SYSTEM[4].bgClass).toBe('bg-emerald-500')
  })

  it('renders tooltip with description when showTooltip is true', () => {
    render(<EvidenceBadge score={4} showTooltip={true} />)

    const tooltip = screen.getByText(
      'Verified by official authorities (police, military, NOTAM)'
    )
    expect(tooltip).toBeInTheDocument()
  })

  it('hides tooltip when showTooltip is false', () => {
    render(<EvidenceBadge score={4} showTooltip={false} />)

    const tooltip = screen.queryByText(
      'Verified by official authorities (police, military, NOTAM)'
    )
    expect(tooltip).not.toBeInTheDocument()
  })

  it('applies correct size classes for small size', () => {
    render(<EvidenceBadge score={4} size="sm" />)

    const badge = screen.getByText('OFFICIAL')
    const container = badge.parentElement
    expect(container).toHaveClass('text-[10px]')
    expect(container).toHaveClass('px-2')
    expect(container).toHaveClass('py-1')
  })

  it('applies correct size classes for medium size', () => {
    render(<EvidenceBadge score={4} size="md" />)

    const badge = screen.getByText('OFFICIAL')
    const container = badge.parentElement
    expect(container).toHaveClass('text-xs')
    expect(container).toHaveClass('px-4')
    expect(container).toHaveClass('py-2')
  })

  it('applies correct size classes for large size', () => {
    render(<EvidenceBadge score={4} size="lg" />)

    const badge = screen.getByText('OFFICIAL')
    const container = badge.parentElement
    expect(container).toHaveClass('text-sm')
    expect(container).toHaveClass('px-5')
    expect(container).toHaveClass('py-2.5')
  })

  it('applies custom className prop', () => {
    render(<EvidenceBadge score={4} className="my-custom-class" />)

    const badge = screen.getByText('OFFICIAL')
    const container = badge.parentElement
    expect(container).toHaveClass('my-custom-class')
  })

  it('has correct ARIA label', () => {
    render(<EvidenceBadge score={4} />)

    const element = screen.getByRole('status')
    expect(element).toHaveAttribute('aria-label', 'Evidence score: OFFICIAL')
  })

  it('renders shield icon for score 4', () => {
    const { container } = render(<EvidenceBadge score={4} />)

    const svg = container.querySelector('svg')
    expect(svg).toBeInTheDocument()
    expect(svg).toHaveClass('w-3.5')
    expect(svg).toHaveClass('h-3.5')
  })

  it('displays all evidence scores correctly', () => {
    const scores = [1, 2, 3, 4] as const

    scores.forEach((score) => {
      const { unmount } = render(<EvidenceBadge score={score} />)
      const config = EVIDENCE_SYSTEM[score]

      const badge = screen.getByText(config.label)
      expect(badge).toBeInTheDocument()

      const container = badge.parentElement
      expect(container).toHaveClass(config.bgClass)

      unmount()
    })
  })
})
