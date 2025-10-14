import L from 'leaflet'
import {
  createIncidentIcon,
  createFacilityIcon,
  createClusterIcon,
} from '../MarkerFactory'
import { EVIDENCE_SYSTEM } from '@/constants/evidence'

// Mock Leaflet
jest.mock('leaflet', () => ({
  divIcon: jest.fn((options) => ({
    options,
    _iconUrl: undefined,
  })),
}))

describe('MarkerFactory', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('createIncidentIcon', () => {
    it('creates icon with correct evidence score', () => {
      createIncidentIcon(4, false)

      expect(L.divIcon).toHaveBeenCalledWith(
        expect.objectContaining({
          className: 'custom-marker',
          iconSize: [38, 38],
          iconAnchor: [19, 19],
        })
      )

      const call = (L.divIcon as jest.Mock).mock.calls[0][0]
      expect(call.html).toContain('4')
    })

    it('applies correct gradient for score 4 (green)', () => {
      createIncidentIcon(4, false)

      const call = (L.divIcon as jest.Mock).mock.calls[0][0]
      const config = EVIDENCE_SYSTEM[4]
      expect(call.html).toContain(config.gradient)
    })

    it('applies correct gradient for score 3 (amber)', () => {
      createIncidentIcon(3, false)

      const call = (L.divIcon as jest.Mock).mock.calls[0][0]
      const config = EVIDENCE_SYSTEM[3]
      expect(call.html).toContain(config.gradient)
    })

    it('uses white border in light mode', () => {
      createIncidentIcon(4, false)

      const call = (L.divIcon as jest.Mock).mock.calls[0][0]
      expect(call.html).toContain('border: 3px solid white')
    })

    it('uses dark border in dark mode', () => {
      createIncidentIcon(4, true)

      const call = (L.divIcon as jest.Mock).mock.calls[0][0]
      expect(call.html).toContain('border: 3px solid #1f2937')
    })

    it('sets correct icon dimensions', () => {
      createIncidentIcon(4, false)

      const call = (L.divIcon as jest.Mock).mock.calls[0][0]
      expect(call.html).toContain('width: 38px')
      expect(call.html).toContain('height: 38px')
    })

    it('applies glow effect from evidence config', () => {
      createIncidentIcon(4, false)

      const call = (L.divIcon as jest.Mock).mock.calls[0][0]
      const config = EVIDENCE_SYSTEM[4]
      expect(call.html).toContain(config.glow)
    })
  })

  describe('createFacilityIcon', () => {
    it('creates icon with correct count', () => {
      createFacilityIcon(5, 'airport', false)

      const call = (L.divIcon as jest.Mock).mock.calls[0][0]
      expect(call.html).toContain('5')
    })

    it('displays airport emoji for airport type', () => {
      createFacilityIcon(3, 'airport', false)

      const call = (L.divIcon as jest.Mock).mock.calls[0][0]
      expect(call.html).toContain('✈️')
    })

    it('displays military emoji for military type', () => {
      createFacilityIcon(2, 'military', false)

      const call = (L.divIcon as jest.Mock).mock.calls[0][0]
      expect(call.html).toContain('🛡️')
    })

    it('uses slate gradient in light mode', () => {
      createFacilityIcon(3, 'airport', false)

      const call = (L.divIcon as jest.Mock).mock.calls[0][0]
      expect(call.html).toContain('linear-gradient(135deg, #64748b 0%, #475569 100%)')
    })

    it('uses darker slate gradient in dark mode', () => {
      createFacilityIcon(3, 'airport', true)

      const call = (L.divIcon as jest.Mock).mock.calls[0][0]
      expect(call.html).toContain('linear-gradient(135deg, #475569 0%, #334155 100%)')
    })

    it('sets correct CSS class', () => {
      createFacilityIcon(3, 'airport', false)

      const call = (L.divIcon as jest.Mock).mock.calls[0][0]
      expect(call.className).toBe('marker-cluster-facility')
    })

    it('sets correct icon size to 50x50', () => {
      createFacilityIcon(3, 'airport', false)

      const call = (L.divIcon as jest.Mock).mock.calls[0][0]
      expect(call.iconSize).toEqual([50, 50])
      expect(call.iconAnchor).toEqual([25, 25])
    })
  })

  describe('createClusterIcon', () => {
    it('creates facility cluster for same asset type', () => {
      const mockCluster = {
        getChildCount: () => 3,
        getAllChildMarkers: () => [
          {
            incidentData: {
              asset_type: 'airport',
              location_name: 'Copenhagen Airport',
              evidence_score: 4,
            },
          },
          {
            incidentData: {
              asset_type: 'airport',
              location_name: 'Copenhagen Airport',
              evidence_score: 3,
            },
          },
          {
            incidentData: {
              asset_type: 'airport',
              location_name: 'Copenhagen Airport',
              evidence_score: 2,
            },
          },
        ],
      }

      createClusterIcon(mockCluster, false)

      const call = (L.divIcon as jest.Mock).mock.calls[0][0]
      expect(call.html).toContain('3')
      expect(call.html).toContain('✈️')
      expect(call.className).toBe('marker-cluster-facility')
    })

    it('uses evidence icon for mixed asset types', () => {
      const mockCluster = {
        getChildCount: () => 2,
        getAllChildMarkers: () => [
          {
            incidentData: {
              asset_type: 'airport',
              evidence_score: 4,
            },
          },
          {
            incidentData: {
              asset_type: 'military',
              evidence_score: 3,
            },
          },
        ],
      }

      createClusterIcon(mockCluster, false)

      const call = (L.divIcon as jest.Mock).mock.calls[0][0]
      // Should use evidence icon for first marker
      expect(call.className).toBe('custom-marker')
    })

    it('handles empty cluster gracefully', () => {
      const mockCluster = {
        getChildCount: () => 0,
        getAllChildMarkers: () => [],
      }

      const icon = createClusterIcon(mockCluster, false)

      expect(icon).toBeDefined()
    })

    it('applies dark mode styling to facility cluster', () => {
      const mockCluster = {
        getChildCount: () => 2,
        getAllChildMarkers: () => [
          {
            incidentData: {
              asset_type: 'airport',
              location_name: 'Test Airport',
              evidence_score: 4,
            },
          },
          {
            incidentData: {
              asset_type: 'airport',
              location_name: 'Test Airport',
              evidence_score: 3,
            },
          },
        ],
      }

      createClusterIcon(mockCluster, true)

      const call = (L.divIcon as jest.Mock).mock.calls[0][0]
      expect(call.html).toContain('linear-gradient(135deg, #475569 0%, #334155 100%)')
    })
  })

  describe('Icon HTML structure', () => {
    it('incident icon has correct HTML structure', () => {
      createIncidentIcon(4, false)

      const call = (L.divIcon as jest.Mock).mock.calls[0][0]
      expect(call.html).toContain('<div style=')
      expect(call.html).toContain('border-radius: 50%')
      expect(call.html).toContain('display: flex')
    })

    it('facility icon has correct HTML structure', () => {
      createFacilityIcon(3, 'airport', false)

      const call = (L.divIcon as jest.Mock).mock.calls[0][0]
      expect(call.html).toContain('<div style=')
      expect(call.html).toContain('flex-direction: column')
      expect(call.html).toContain('cursor: pointer')
    })
  })

  describe('Evidence system integration', () => {
    it('uses evidence constants from constants/evidence.ts', () => {
      createIncidentIcon(4, false)

      const call = (L.divIcon as jest.Mock).mock.calls[0][0]
      const config = EVIDENCE_SYSTEM[4]

      expect(call.html).toContain(config.gradient)
      expect(call.html).toContain(config.glow)
    })

    it('applies correct colors for all evidence scores', () => {
      const scores = [1, 2, 3, 4] as const

      scores.forEach((score) => {
        jest.clearAllMocks()
        createIncidentIcon(score, false)

        const call = (L.divIcon as jest.Mock).mock.calls[0][0]
        const config = EVIDENCE_SYSTEM[score]

        expect(call.html).toContain(config.gradient)
        expect(call.html).toContain(String(score))
      })
    })
  })
})
