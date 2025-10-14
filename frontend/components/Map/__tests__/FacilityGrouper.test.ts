import {
  groupIncidentsByFacility,
  getFacilityEmoji,
  FACILITY_EMOJI,
} from '../FacilityGrouper'
import type { Incident } from '@/types'

describe('FacilityGrouper', () => {
  const createMockIncident = (
    id: string,
    lat: number,
    lon: number,
    asset_type?: string
  ): Incident =>
    ({
      id,
      lat,
      lon,
      asset_type,
      title: `Test Incident ${id}`,
      evidence_score: 3,
    } as Incident)

  describe('groupIncidentsByFacility', () => {
    it('groups incidents by location and asset type', () => {
      const incidents = [
        createMockIncident('1', 55.618, 12.656, 'airport'),
        createMockIncident('2', 55.618, 12.656, 'airport'),
        createMockIncident('3', 55.618, 12.656, 'airport'),
      ]

      const { facilityGroups, singleIncidents } =
        groupIncidentsByFacility(incidents)

      const key = '55.618,12.656-airport'
      expect(facilityGroups[key]).toHaveLength(3)
      expect(singleIncidents).toHaveLength(0)
    })

    it('uses 3 decimal precision for coordinates', () => {
      const incidents = [
        createMockIncident('1', 55.618123, 12.656789, 'airport'),
        createMockIncident('2', 55.618456, 12.656321, 'airport'),
      ]

      const { facilityGroups } = groupIncidentsByFacility(incidents)

      // Both should round to 55.618,12.656
      const key = '55.618,12.657-airport'
      expect(Object.keys(facilityGroups)).toContain(key)
    })

    it('separates incidents by asset type', () => {
      const incidents = [
        createMockIncident('1', 55.618, 12.656, 'airport'),
        createMockIncident('2', 55.618, 12.656, 'harbor'),
      ]

      const { facilityGroups } = groupIncidentsByFacility(incidents)

      expect(Object.keys(facilityGroups)).toHaveLength(2)
      expect(facilityGroups['55.618,12.656-airport']).toHaveLength(1)
      expect(facilityGroups['55.618,12.656-harbor']).toHaveLength(1)
    })

    it('returns empty arrays for no incidents', () => {
      const { facilityGroups, singleIncidents } = groupIncidentsByFacility([])

      expect(Object.keys(facilityGroups)).toHaveLength(0)
      expect(singleIncidents).toHaveLength(0)
    })

    it('puts incidents without asset_type in singleIncidents', () => {
      const incidents = [
        createMockIncident('1', 55.618, 12.656, 'airport'),
        createMockIncident('2', 55.619, 12.657, undefined),
        createMockIncident('3', 55.620, 12.658, undefined),
      ]

      const { facilityGroups, singleIncidents } =
        groupIncidentsByFacility(incidents)

      expect(Object.keys(facilityGroups)).toHaveLength(1)
      expect(singleIncidents).toHaveLength(2)
    })

    it('handles mixed facilities at different locations', () => {
      const incidents = [
        createMockIncident('1', 55.618, 12.656, 'airport'),
        createMockIncident('2', 55.618, 12.656, 'airport'),
        createMockIncident('3', 60.123, 10.456, 'military'),
        createMockIncident('4', 60.123, 10.456, 'military'),
      ]

      const { facilityGroups } = groupIncidentsByFacility(incidents)

      expect(Object.keys(facilityGroups)).toHaveLength(2)
      expect(facilityGroups['55.618,12.656-airport']).toHaveLength(2)
      expect(facilityGroups['60.123,10.456-military']).toHaveLength(2)
    })
  })

  describe('getFacilityEmoji', () => {
    it('returns correct emoji for airport', () => {
      expect(getFacilityEmoji('airport')).toBe('✈️')
    })

    it('returns correct emoji for harbor', () => {
      expect(getFacilityEmoji('harbor')).toBe('⚓')
    })

    it('returns correct emoji for military', () => {
      expect(getFacilityEmoji('military')).toBe('🛡️')
    })

    it('returns correct emoji for powerplant', () => {
      expect(getFacilityEmoji('powerplant')).toBe('⚡')
    })

    it('returns correct emoji for bridge', () => {
      expect(getFacilityEmoji('bridge')).toBe('🌉')
    })

    it('returns default emoji for unknown type', () => {
      expect(getFacilityEmoji('unknown')).toBe('📍')
    })

    it('returns default emoji for undefined', () => {
      expect(getFacilityEmoji(undefined)).toBe('📍')
    })

    it('returns default emoji for other', () => {
      expect(getFacilityEmoji('other')).toBe('📍')
    })
  })

  describe('FACILITY_EMOJI constant', () => {
    it('contains all expected asset types', () => {
      expect(FACILITY_EMOJI).toHaveProperty('airport')
      expect(FACILITY_EMOJI).toHaveProperty('military')
      expect(FACILITY_EMOJI).toHaveProperty('harbor')
      expect(FACILITY_EMOJI).toHaveProperty('powerplant')
      expect(FACILITY_EMOJI).toHaveProperty('bridge')
      expect(FACILITY_EMOJI).toHaveProperty('other')
    })

    it('has correct emoji values', () => {
      expect(FACILITY_EMOJI.airport).toBe('✈️')
      expect(FACILITY_EMOJI.military).toBe('🛡️')
      expect(FACILITY_EMOJI.harbor).toBe('⚓')
      expect(FACILITY_EMOJI.powerplant).toBe('⚡')
      expect(FACILITY_EMOJI.bridge).toBe('🌉')
      expect(FACILITY_EMOJI.other).toBe('📍')
    })
  })
})
