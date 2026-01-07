import type { Incident, IncidentSource } from '@/types'
import {
  formatIncidentsToCSV,
  formatIncidentsToJSON,
  downloadFile,
  generateExportFilename,
} from '../export'

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

/**
 * Helper to create a source
 */
function createMockSource(overrides: Partial<IncidentSource> = {}): IncidentSource {
  return {
    source_url: 'https://example.com/source',
    source_type: 'news',
    source_title: 'News Article',
    ...overrides,
  }
}

describe('Export Utilities', () => {
  describe('formatIncidentsToCSV', () => {
    it('returns only headers for empty incident array', () => {
      const csv = formatIncidentsToCSV([])
      expect(csv).toBe('Title,Date,Location,Country,Evidence Score,Sources Count,Narrative')
    })

    it('formats a single incident correctly', () => {
      const incident = createMockIncident({
        title: 'Drone Spotted',
        occurred_at: '2025-06-15T10:30:00Z',
        location_name: 'Copenhagen Airport',
        country: 'DK',
        evidence_score: 3,
        sources: [createMockSource()],
        narrative: 'A drone was spotted.',
      })

      const csv = formatIncidentsToCSV([incident])
      const lines = csv.split('\n')

      expect(lines).toHaveLength(2)
      expect(lines[0]).toBe('Title,Date,Location,Country,Evidence Score,Sources Count,Narrative')
      expect(lines[1]).toContain('Drone Spotted')
      expect(lines[1]).toContain('Copenhagen Airport')
      expect(lines[1]).toContain('Denmark')
      expect(lines[1]).toContain('3')
      expect(lines[1]).toContain('1')
    })

    it('formats multiple incidents correctly', () => {
      const incidents = [
        createMockIncident({
          id: '1',
          title: 'First Incident',
          country: 'DK',
        }),
        createMockIncident({
          id: '2',
          title: 'Second Incident',
          country: 'SE',
        }),
        createMockIncident({
          id: '3',
          title: 'Third Incident',
          country: 'NO',
        }),
      ]

      const csv = formatIncidentsToCSV(incidents)
      const lines = csv.split('\n')

      expect(lines).toHaveLength(4) // 1 header + 3 data rows
      expect(lines[1]).toContain('First Incident')
      expect(lines[1]).toContain('Denmark')
      expect(lines[2]).toContain('Second Incident')
      expect(lines[2]).toContain('Sweden')
      expect(lines[3]).toContain('Third Incident')
      expect(lines[3]).toContain('Norway')
    })

    it('escapes commas in values', () => {
      const incident = createMockIncident({
        title: 'Incident, with comma',
        narrative: 'Drone spotted, over airport, near runway.',
      })

      const csv = formatIncidentsToCSV([incident])

      // Values with commas should be wrapped in quotes
      expect(csv).toContain('"Incident, with comma"')
      expect(csv).toContain('"Drone spotted, over airport, near runway."')
    })

    it('escapes double quotes in values', () => {
      const incident = createMockIncident({
        title: 'Incident with "quotes"',
        narrative: 'Witness said "I saw a drone".',
      })

      const csv = formatIncidentsToCSV([incident])

      // Quotes should be doubled and value wrapped in quotes
      expect(csv).toContain('"Incident with ""quotes"""')
      expect(csv).toContain('"Witness said ""I saw a drone""."')
    })

    it('escapes newlines in values', () => {
      const incident = createMockIncident({
        narrative: 'First line.\nSecond line.',
      })

      const csv = formatIncidentsToCSV([incident])

      // Newlines should cause value to be wrapped in quotes
      expect(csv).toContain('"First line.\nSecond line."')
    })

    it('handles carriage returns in values', () => {
      const incident = createMockIncident({
        narrative: 'Line with\r\nWindows newline.',
      })

      const csv = formatIncidentsToCSV([incident])

      // Should be wrapped in quotes
      expect(csv).toMatch(/"Line with\r\nWindows newline."/)
    })

    it('handles combined special characters', () => {
      const incident = createMockIncident({
        title: 'Complex "title", with\nmultiple issues',
      })

      const csv = formatIncidentsToCSV([incident])

      // Should escape quotes AND wrap in quotes
      expect(csv).toContain('"Complex ""title"", with\nmultiple issues"')
    })

    it('handles incidents with no sources', () => {
      const incident = createMockIncident({
        sources: [],
      })

      const csv = formatIncidentsToCSV([incident])
      const lines = csv.split('\n')

      // Sources count should be 0
      expect(lines[1]).toContain(',0,')
    })

    it('handles incidents with undefined sources', () => {
      const incident = createMockIncident()
      // Force undefined sources
      ;(incident as { sources: undefined }).sources = undefined

      const csv = formatIncidentsToCSV([incident])
      const lines = csv.split('\n')

      // Sources count should be 0
      expect(lines[1]).toContain(',0,')
    })

    it('handles incidents with empty narrative', () => {
      const incident = createMockIncident({
        narrative: '',
      })

      const csv = formatIncidentsToCSV([incident])
      const lines = csv.split('\n')

      // Should end with empty value
      expect(lines[1]).toMatch(/,\d+,$/)
    })

    it('handles incidents with undefined narrative', () => {
      const incident = createMockIncident()
      ;(incident as { narrative?: string }).narrative = undefined

      const csv = formatIncidentsToCSV([incident])

      // Should not throw and should have empty narrative field
      expect(csv).toBeDefined()
    })

    it('cleans narratives with Twitter handles and URLs', () => {
      const incident = createMockIncident({
        narrative: 'Drone spotted @user123 check https://example.com #drones',
      })

      const csv = formatIncidentsToCSV([incident])

      // cleanNarrative should remove handles, URLs, and hashtags
      expect(csv).toContain('Drone spotted')
      expect(csv).not.toContain('@user123')
      expect(csv).not.toContain('https://example.com')
      expect(csv).not.toContain('#drones')
    })

    it('uses formatCountry for country codes', () => {
      const incidents = [
        createMockIncident({ country: 'DK' }),
        createMockIncident({ country: 'SE' }),
        createMockIncident({ country: 'GB' }),
      ]

      const csv = formatIncidentsToCSV(incidents)

      expect(csv).toContain('Denmark')
      expect(csv).toContain('Sweden')
      expect(csv).toContain('United Kingdom')
    })

    it('uses extractLocation for location extraction', () => {
      const incident = createMockIncident({
        location_name: 'Kastrup',
      })

      const csv = formatIncidentsToCSV([incident])

      expect(csv).toContain('Kastrup')
    })
  })

  describe('formatIncidentsToJSON', () => {
    it('returns empty array for no incidents', () => {
      const json = formatIncidentsToJSON([])
      expect(json).toBe('[]')
      expect(JSON.parse(json)).toEqual([])
    })

    it('formats a single incident correctly', () => {
      const incident = createMockIncident({
        title: 'Test Incident',
        occurred_at: '2025-06-15T10:30:00Z',
        location_name: 'Copenhagen Airport',
        country: 'DK',
        evidence_score: 3,
        lat: 55.6181,
        lon: 12.6561,
        narrative: 'A drone was spotted.',
        sources: [
          {
            source_url: 'https://example.com/news',
            source_type: 'news',
            source_title: 'News Article',
          },
        ],
      })

      const json = formatIncidentsToJSON([incident])
      const parsed = JSON.parse(json)

      expect(parsed).toHaveLength(1)
      expect(parsed[0]).toEqual({
        title: 'Test Incident',
        date: expect.any(String),
        location: 'Copenhagen Airport',
        country: 'Denmark',
        evidenceScore: 3,
        sourcesCount: 1,
        narrative: 'A drone was spotted.',
        coordinates: {
          lat: 55.6181,
          lon: 12.6561,
        },
        sources: [
          {
            title: 'News Article',
            url: 'https://example.com/news',
            type: 'news',
          },
        ],
      })
    })

    it('formats multiple incidents correctly', () => {
      const incidents = [
        createMockIncident({ id: '1', title: 'First' }),
        createMockIncident({ id: '2', title: 'Second' }),
      ]

      const json = formatIncidentsToJSON(incidents)
      const parsed = JSON.parse(json)

      expect(parsed).toHaveLength(2)
      expect(parsed[0].title).toBe('First')
      expect(parsed[1].title).toBe('Second')
    })

    it('outputs valid JSON with proper formatting', () => {
      const incident = createMockIncident()
      const json = formatIncidentsToJSON([incident])

      // Should be valid JSON
      expect(() => JSON.parse(json)).not.toThrow()

      // Should be pretty-printed (contain newlines)
      expect(json).toContain('\n')

      // Should have 2-space indentation
      expect(json).toContain('  ')
    })

    it('handles incidents with multiple sources', () => {
      const incident = createMockIncident({
        sources: [
          { source_url: 'https://source1.com', source_type: 'news', source_title: 'Source 1' },
          { source_url: 'https://source2.com', source_type: 'police', source_title: 'Source 2' },
          { source_url: 'https://source3.com', source_type: 'social', source_title: 'Source 3' },
        ],
      })

      const json = formatIncidentsToJSON([incident])
      const parsed = JSON.parse(json)

      expect(parsed[0].sourcesCount).toBe(3)
      expect(parsed[0].sources).toHaveLength(3)
      expect(parsed[0].sources[0].url).toBe('https://source1.com')
      expect(parsed[0].sources[1].type).toBe('police')
    })

    it('handles incidents with no sources', () => {
      const incident = createMockIncident({
        sources: [],
      })

      const json = formatIncidentsToJSON([incident])
      const parsed = JSON.parse(json)

      expect(parsed[0].sourcesCount).toBe(0)
      expect(parsed[0].sources).toEqual([])
    })

    it('handles incidents with undefined sources', () => {
      const incident = createMockIncident()
      ;(incident as { sources: undefined }).sources = undefined

      const json = formatIncidentsToJSON([incident])
      const parsed = JSON.parse(json)

      expect(parsed[0].sourcesCount).toBe(0)
      expect(parsed[0].sources).toEqual([])
    })

    it('includes coordinates', () => {
      const incident = createMockIncident({
        lat: 55.6181,
        lon: 12.6561,
      })

      const json = formatIncidentsToJSON([incident])
      const parsed = JSON.parse(json)

      expect(parsed[0].coordinates).toEqual({
        lat: 55.6181,
        lon: 12.6561,
      })
    })

    it('cleans narratives', () => {
      const incident = createMockIncident({
        narrative: 'Drone spotted @user123 https://example.com #drone',
      })

      const json = formatIncidentsToJSON([incident])
      const parsed = JSON.parse(json)

      expect(parsed[0].narrative).toBe('Drone spotted')
    })

    it('uses formatCountry for country codes', () => {
      const incident = createMockIncident({ country: 'SE' })

      const json = formatIncidentsToJSON([incident])
      const parsed = JSON.parse(json)

      expect(parsed[0].country).toBe('Sweden')
    })

    it('handles sources without title', () => {
      const incident = createMockIncident({
        sources: [
          {
            source_url: 'https://example.com',
            source_type: 'news',
            // no source_title
          },
        ],
      })

      const json = formatIncidentsToJSON([incident])
      const parsed = JSON.parse(json)

      expect(parsed[0].sources[0].title).toBeUndefined()
      expect(parsed[0].sources[0].url).toBe('https://example.com')
    })
  })

  describe('downloadFile', () => {
    let createElementSpy: jest.SpyInstance
    let appendChildSpy: jest.SpyInstance
    let removeChildSpy: jest.SpyInstance
    let createObjectURLSpy: jest.SpyInstance
    let revokeObjectURLSpy: jest.SpyInstance
    let mockLink: {
      href: string
      download: string
      style: { display: string }
      click: jest.Mock
    }

    beforeEach(() => {
      // Create mock link element
      mockLink = {
        href: '',
        download: '',
        style: { display: '' },
        click: jest.fn(),
      }

      // Mock document.createElement
      createElementSpy = jest.spyOn(document, 'createElement').mockReturnValue(mockLink as unknown as HTMLAnchorElement)

      // Mock document.body methods
      appendChildSpy = jest.spyOn(document.body, 'appendChild').mockImplementation((node) => node)
      removeChildSpy = jest.spyOn(document.body, 'removeChild').mockImplementation((node) => node)

      // Mock URL methods
      createObjectURLSpy = jest.spyOn(URL, 'createObjectURL').mockReturnValue('blob:mock-url')
      revokeObjectURLSpy = jest.spyOn(URL, 'revokeObjectURL').mockImplementation()
    })

    afterEach(() => {
      createElementSpy.mockRestore()
      appendChildSpy.mockRestore()
      removeChildSpy.mockRestore()
      createObjectURLSpy.mockRestore()
      revokeObjectURLSpy.mockRestore()
    })

    it('creates a link element', () => {
      downloadFile('content', 'test.csv', 'text/csv')
      expect(createElementSpy).toHaveBeenCalledWith('a')
    })

    it('sets href to blob URL', () => {
      downloadFile('content', 'test.csv', 'text/csv')
      expect(mockLink.href).toBe('blob:mock-url')
    })

    it('sets download filename', () => {
      downloadFile('content', 'my-export.csv', 'text/csv')
      expect(mockLink.download).toBe('my-export.csv')
    })

    it('hides the link element', () => {
      downloadFile('content', 'test.csv', 'text/csv')
      expect(mockLink.style.display).toBe('none')
    })

    it('appends link to document body', () => {
      downloadFile('content', 'test.csv', 'text/csv')
      expect(appendChildSpy).toHaveBeenCalledWith(mockLink)
    })

    it('clicks the link to trigger download', () => {
      downloadFile('content', 'test.csv', 'text/csv')
      expect(mockLink.click).toHaveBeenCalled()
    })

    it('removes link from document body after click', () => {
      downloadFile('content', 'test.csv', 'text/csv')
      expect(removeChildSpy).toHaveBeenCalledWith(mockLink)
    })

    it('revokes the object URL for cleanup', () => {
      downloadFile('content', 'test.csv', 'text/csv')
      expect(revokeObjectURLSpy).toHaveBeenCalledWith('blob:mock-url')
    })

    it('creates blob with correct MIME type for CSV', () => {
      downloadFile('csv content', 'test.csv', 'text/csv')
      expect(createObjectURLSpy).toHaveBeenCalledWith(
        expect.any(Blob)
      )
    })

    it('creates blob with correct MIME type for JSON', () => {
      downloadFile('{"data": "json"}', 'test.json', 'application/json')
      expect(createObjectURLSpy).toHaveBeenCalledWith(
        expect.any(Blob)
      )
    })

    it('handles empty content', () => {
      downloadFile('', 'empty.csv', 'text/csv')

      expect(createElementSpy).toHaveBeenCalled()
      expect(mockLink.click).toHaveBeenCalled()
    })
  })

  describe('generateExportFilename', () => {
    let dateSpy: jest.SpyInstance

    afterEach(() => {
      if (dateSpy) {
        dateSpy.mockRestore()
      }
    })

    it('generates CSV filename with current date', () => {
      // Mock the Date to get consistent results
      const mockDate = new Date('2025-06-15T12:00:00Z')
      dateSpy = jest.spyOn(global, 'Date').mockImplementation(() => mockDate)

      const filename = generateExportFilename('csv')
      expect(filename).toBe('dronewatch-incidents-2025-06-15.csv')
    })

    it('generates JSON filename with current date', () => {
      const mockDate = new Date('2025-06-15T12:00:00Z')
      dateSpy = jest.spyOn(global, 'Date').mockImplementation(() => mockDate)

      const filename = generateExportFilename('json')
      expect(filename).toBe('dronewatch-incidents-2025-06-15.json')
    })

    it('pads single-digit months with zero', () => {
      const mockDate = new Date('2025-01-05T12:00:00Z')
      dateSpy = jest.spyOn(global, 'Date').mockImplementation(() => mockDate)

      const filename = generateExportFilename('csv')
      expect(filename).toBe('dronewatch-incidents-2025-01-05.csv')
    })

    it('pads single-digit days with zero', () => {
      const mockDate = new Date('2025-12-01T12:00:00Z')
      dateSpy = jest.spyOn(global, 'Date').mockImplementation(() => mockDate)

      const filename = generateExportFilename('csv')
      expect(filename).toBe('dronewatch-incidents-2025-12-01.csv')
    })

    it('handles any extension', () => {
      const mockDate = new Date('2025-06-15T12:00:00Z')
      dateSpy = jest.spyOn(global, 'Date').mockImplementation(() => mockDate)

      const filename = generateExportFilename('txt')
      expect(filename).toBe('dronewatch-incidents-2025-06-15.txt')
    })

    it('generates filename in correct format', () => {
      const filename = generateExportFilename('csv')
      expect(filename).toMatch(/^dronewatch-incidents-\d{4}-\d{2}-\d{2}\.csv$/)
    })
  })

  describe('Edge Cases', () => {
    it('handles incident with all optional fields missing', () => {
      const minimalIncident: Incident = {
        id: '1',
        title: 'Minimal',
        occurred_at: '2025-06-15T10:00:00Z',
        first_seen_at: '2025-06-15T10:00:00Z',
        last_seen_at: '2025-06-15T10:00:00Z',
        lat: 0,
        lon: 0,
        status: 'active',
        evidence_score: 1,
        country: 'DK',
        sources: [],
      }

      // Should not throw for CSV
      expect(() => formatIncidentsToCSV([minimalIncident])).not.toThrow()

      // Should not throw for JSON
      expect(() => formatIncidentsToJSON([minimalIncident])).not.toThrow()
    })

    it('handles very long narratives', () => {
      const longNarrative = 'A '.repeat(1000) + 'drone was spotted.'
      const incident = createMockIncident({
        narrative: longNarrative,
      })

      const csv = formatIncidentsToCSV([incident])
      const json = formatIncidentsToJSON([incident])

      expect(csv.length).toBeGreaterThan(1000)
      expect(JSON.parse(json)[0].narrative.length).toBeGreaterThan(1000)
    })

    it('handles special Unicode characters', () => {
      const incident = createMockIncident({
        title: 'Incident über Flughafen',
        narrative: 'Drohne gesichtet über München. 日本語テスト.',
      })

      const csv = formatIncidentsToCSV([incident])
      const json = formatIncidentsToJSON([incident])

      expect(csv).toContain('über')
      expect(csv).toContain('München')
      expect(JSON.parse(json)[0].narrative).toContain('日本語テスト')
    })

    it('handles unknown country codes', () => {
      const incident = createMockIncident({
        country: 'XX', // Unknown code
      })

      const csv = formatIncidentsToCSV([incident])
      const json = formatIncidentsToJSON([incident])

      // Should fall back to the code itself
      expect(csv).toContain('XX')
      expect(JSON.parse(json)[0].country).toBe('XX')
    })

    it('CSV and JSON have consistent data for same incident', () => {
      const incident = createMockIncident({
        title: 'Consistency Test',
        country: 'DK',
        evidence_score: 3,
        sources: [createMockSource(), createMockSource()],
      })

      const csv = formatIncidentsToCSV([incident])
      const json = formatIncidentsToJSON([incident])
      const parsed = JSON.parse(json)

      // Both should contain same title
      expect(csv).toContain('Consistency Test')
      expect(parsed[0].title).toBe('Consistency Test')

      // Both should have same country (formatted)
      expect(csv).toContain('Denmark')
      expect(parsed[0].country).toBe('Denmark')

      // Both should have same evidence score
      expect(csv).toContain(',3,')
      expect(parsed[0].evidenceScore).toBe(3)

      // Both should have same sources count
      expect(csv).toContain(',2,')
      expect(parsed[0].sourcesCount).toBe(2)
    })
  })
})
