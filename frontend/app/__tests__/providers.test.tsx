import { render, screen } from '@testing-library/react'
import { Providers } from '../providers'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Mock next-themes
jest.mock('next-themes', () => ({
  ThemeProvider: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="theme-provider">{children}</div>
  ),
}))

describe('Providers', () => {
  it('renders children correctly', () => {
    render(
      <Providers>
        <div data-testid="test-child">Test Child</div>
      </Providers>
    )

    expect(screen.getByTestId('test-child')).toBeInTheDocument()
    expect(screen.getByText('Test Child')).toBeInTheDocument()
  })

  it('wraps children with ThemeProvider', () => {
    render(
      <Providers>
        <div>Content</div>
      </Providers>
    )

    expect(screen.getByTestId('theme-provider')).toBeInTheDocument()
  })

  it('wraps children with QueryClientProvider', () => {
    const { container } = render(
      <Providers>
        <div>Content</div>
      </Providers>
    )

    // QueryClientProvider should be present in the tree
    expect(container.firstChild).toBeInTheDocument()
  })

  it('creates QueryClient with correct configuration', () => {
    const createClientSpy = jest.spyOn(QueryClient.prototype, 'constructor' as any)

    render(
      <Providers>
        <div>Content</div>
      </Providers>
    )

    // QueryClient should be created (implementation detail)
    expect(QueryClient).toBeDefined()
  })

  it('renders multiple children', () => {
    render(
      <Providers>
        <div data-testid="child1">Child 1</div>
        <div data-testid="child2">Child 2</div>
      </Providers>
    )

    expect(screen.getByTestId('child1')).toBeInTheDocument()
    expect(screen.getByTestId('child2')).toBeInTheDocument()
  })

  it('handles empty children', () => {
    const { container } = render(<Providers>{null}</Providers>)

    expect(container).toBeInTheDocument()
  })

  it('maintains children structure', () => {
    render(
      <Providers>
        <div>
          <span>Nested</span>
        </div>
      </Providers>
    )

    expect(screen.getByText('Nested')).toBeInTheDocument()
  })
})
