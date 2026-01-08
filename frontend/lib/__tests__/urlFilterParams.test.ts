import {
  parseMinEvidence,
  parseDateRange,
  parseAssetType,
  parseCountry,
  parseStatus,
  parseFilterParams,
  serializeFilterParams,
  DEFAULT_FILTER_STATE,
  VALID_DATE_RANGES,
  MIN_EVIDENCE_RANGE,
  URL_PARAM_KEYS,
} from '../urlFilterParams'
import type { FilterState } from '@/types'

describe('urlFilterParams', () => {
  describe('parseMinEvidence', () => {
    describe('valid values', () => {
      it('parses valid integer 1', () => {
        expect(parseMinEvidence('1')).toBe(1)
      })

      it('parses valid integer 2', () => {
        expect(parseMinEvidence('2')).toBe(2)
      })

      it('parses valid integer 3', () => {
        expect(parseMinEvidence('3')).toBe(3)
      })

      it('parses valid integer 4', () => {
        expect(parseMinEvidence('4')).toBe(4)
      })

      it('handles leading/trailing whitespace', () => {
        expect(parseMinEvidence('  2  ')).toBe(2)
      })
    })

    describe('boundary values', () => {
      it('accepts minimum boundary value (1)', () => {
        expect(parseMinEvidence('1')).toBe(MIN_EVIDENCE_RANGE.min)
      })

      it('accepts maximum boundary value (4)', () => {
        expect(parseMinEvidence('4')).toBe(MIN_EVIDENCE_RANGE.max)
      })

      it('rejects value below minimum (0)', () => {
        expect(parseMinEvidence('0')).toBe(DEFAULT_FILTER_STATE.minEvidence)
      })

      it('rejects value above maximum (5)', () => {
        expect(parseMinEvidence('5')).toBe(DEFAULT_FILTER_STATE.minEvidence)
      })

      it('rejects negative values', () => {
        expect(parseMinEvidence('-1')).toBe(DEFAULT_FILTER_STATE.minEvidence)
      })

      it('rejects large values', () => {
        expect(parseMinEvidence('100')).toBe(DEFAULT_FILTER_STATE.minEvidence)
      })
    })

    describe('invalid values', () => {
      it('returns default for null', () => {
        expect(parseMinEvidence(null)).toBe(DEFAULT_FILTER_STATE.minEvidence)
      })

      it('returns default for empty string', () => {
        expect(parseMinEvidence('')).toBe(DEFAULT_FILTER_STATE.minEvidence)
      })

      it('returns default for whitespace-only string', () => {
        expect(parseMinEvidence('   ')).toBe(DEFAULT_FILTER_STATE.minEvidence)
      })

      it('returns default for non-numeric string', () => {
        expect(parseMinEvidence('abc')).toBe(DEFAULT_FILTER_STATE.minEvidence)
      })

      it('returns default for float values', () => {
        expect(parseMinEvidence('2.5')).toBe(DEFAULT_FILTER_STATE.minEvidence)
      })

      it('returns default for NaN', () => {
        expect(parseMinEvidence('NaN')).toBe(DEFAULT_FILTER_STATE.minEvidence)
      })

      it('returns default for Infinity', () => {
        expect(parseMinEvidence('Infinity')).toBe(DEFAULT_FILTER_STATE.minEvidence)
      })
    })

    describe('XSS/malicious input', () => {
      it('handles script tag injection', () => {
        expect(parseMinEvidence('<script>alert("xss")</script>')).toBe(
          DEFAULT_FILTER_STATE.minEvidence
        )
      })

      it('handles URL encoded input', () => {
        expect(parseMinEvidence('%3Cscript%3E')).toBe(
          DEFAULT_FILTER_STATE.minEvidence
        )
      })

      it('handles SQL injection attempts', () => {
        expect(parseMinEvidence("1'; DROP TABLE users;--")).toBe(
          DEFAULT_FILTER_STATE.minEvidence
        )
      })

      it('handles unicode characters', () => {
        expect(parseMinEvidence('٢')).toBe(DEFAULT_FILTER_STATE.minEvidence)
      })
    })
  })

  describe('parseDateRange', () => {
    describe('valid values', () => {
      it.each(VALID_DATE_RANGES)('parses valid dateRange "%s"', (value) => {
        expect(parseDateRange(value)).toBe(value)
      })

      it('handles case insensitivity - uppercase', () => {
        expect(parseDateRange('WEEK')).toBe('week')
      })

      it('handles case insensitivity - mixed case', () => {
        expect(parseDateRange('Week')).toBe('week')
      })

      it('handles leading/trailing whitespace', () => {
        expect(parseDateRange('  month  ')).toBe('month')
      })
    })

    describe('invalid values', () => {
      it('returns default for null', () => {
        expect(parseDateRange(null)).toBe(DEFAULT_FILTER_STATE.dateRange)
      })

      it('returns default for empty string', () => {
        expect(parseDateRange('')).toBe(DEFAULT_FILTER_STATE.dateRange)
      })

      it('returns default for whitespace-only string', () => {
        expect(parseDateRange('   ')).toBe(DEFAULT_FILTER_STATE.dateRange)
      })

      it('returns default for invalid value', () => {
        expect(parseDateRange('year')).toBe(DEFAULT_FILTER_STATE.dateRange)
      })

      it('returns default for numeric string', () => {
        expect(parseDateRange('7')).toBe(DEFAULT_FILTER_STATE.dateRange)
      })
    })

    describe('XSS/malicious input', () => {
      it('handles script tag injection', () => {
        expect(parseDateRange('<script>alert("xss")</script>')).toBe(
          DEFAULT_FILTER_STATE.dateRange
        )
      })

      it('handles XSS with valid value suffix', () => {
        expect(parseDateRange('week<script>')).toBe(
          DEFAULT_FILTER_STATE.dateRange
        )
      })
    })
  })

  describe('parseAssetType', () => {
    describe('valid values', () => {
      it('parses airport asset type', () => {
        expect(parseAssetType('airport')).toBe('airport')
      })

      it('parses harbor asset type', () => {
        expect(parseAssetType('harbor')).toBe('harbor')
      })

      it('parses military asset type', () => {
        expect(parseAssetType('military')).toBe('military')
      })

      it('parses powerplant asset type', () => {
        expect(parseAssetType('powerplant')).toBe('powerplant')
      })

      it('handles leading/trailing whitespace', () => {
        expect(parseAssetType('  airport  ')).toBe('airport')
      })
    })

    describe('null case handling', () => {
      it('returns null for null input', () => {
        expect(parseAssetType(null)).toBeNull()
      })

      it('returns null for empty string', () => {
        expect(parseAssetType('')).toBeNull()
      })

      it('returns null for whitespace-only string', () => {
        expect(parseAssetType('   ')).toBeNull()
      })

      it('returns null for "null" string', () => {
        expect(parseAssetType('null')).toBeNull()
      })

      it('returns null for "undefined" string', () => {
        expect(parseAssetType('undefined')).toBeNull()
      })

      it('returns null for "none" string', () => {
        expect(parseAssetType('none')).toBeNull()
      })
    })

    describe('XSS/malicious input', () => {
      it('returns trimmed value for script injection (relies on downstream sanitization)', () => {
        // Note: The parser returns the trimmed value; XSS prevention should happen at render
        const result = parseAssetType('<script>')
        expect(result).toBe('<script>')
      })
    })
  })

  describe('parseCountry', () => {
    describe('valid values', () => {
      it('parses country code', () => {
        expect(parseCountry('DK')).toBe('DK')
      })

      it('parses "all" value', () => {
        expect(parseCountry('all')).toBe('all')
      })

      it('handles leading/trailing whitespace', () => {
        expect(parseCountry('  DK  ')).toBe('DK')
      })

      it('preserves case', () => {
        expect(parseCountry('dk')).toBe('dk')
      })
    })

    describe('invalid values', () => {
      it('returns default for null', () => {
        expect(parseCountry(null)).toBe(DEFAULT_FILTER_STATE.country)
      })

      it('returns default for empty string', () => {
        expect(parseCountry('')).toBe(DEFAULT_FILTER_STATE.country)
      })

      it('returns default for whitespace-only string', () => {
        expect(parseCountry('   ')).toBe(DEFAULT_FILTER_STATE.country)
      })
    })
  })

  describe('parseStatus', () => {
    describe('valid values', () => {
      it('parses "active" status', () => {
        expect(parseStatus('active')).toBe('active')
      })

      it('parses "resolved" status', () => {
        expect(parseStatus('resolved')).toBe('resolved')
      })

      it('parses "unconfirmed" status', () => {
        expect(parseStatus('unconfirmed')).toBe('unconfirmed')
      })

      it('parses "all" value', () => {
        expect(parseStatus('all')).toBe('all')
      })

      it('handles leading/trailing whitespace', () => {
        expect(parseStatus('  active  ')).toBe('active')
      })
    })

    describe('invalid values', () => {
      it('returns default for null', () => {
        expect(parseStatus(null)).toBe(DEFAULT_FILTER_STATE.status)
      })

      it('returns default for empty string', () => {
        expect(parseStatus('')).toBe(DEFAULT_FILTER_STATE.status)
      })

      it('returns default for whitespace-only string', () => {
        expect(parseStatus('   ')).toBe(DEFAULT_FILTER_STATE.status)
      })
    })
  })

  describe('parseFilterParams', () => {
    describe('full parameter parsing', () => {
      it('parses all valid parameters', () => {
        const params = new URLSearchParams(
          'min_evidence=3&country=DK&status=active&asset_type=airport&date_range=week'
        )
        const result = parseFilterParams(params)

        expect(result).toEqual({
          minEvidence: 3,
          country: 'DK',
          status: 'active',
          assetType: 'airport',
          dateRange: 'week',
        })
      })

      it('returns defaults for empty params', () => {
        const params = new URLSearchParams('')
        const result = parseFilterParams(params)

        expect(result).toEqual(DEFAULT_FILTER_STATE)
      })

      it('handles partial params with defaults', () => {
        const params = new URLSearchParams('country=SE&min_evidence=2')
        const result = parseFilterParams(params)

        expect(result).toEqual({
          minEvidence: 2,
          country: 'SE',
          status: 'all',
          assetType: null,
          dateRange: 'all',
        })
      })
    })

    describe('mixed valid/invalid params', () => {
      it('uses defaults for invalid values while keeping valid ones', () => {
        const params = new URLSearchParams(
          'min_evidence=invalid&country=DK&date_range=year'
        )
        const result = parseFilterParams(params)

        expect(result).toEqual({
          minEvidence: 1, // default due to invalid
          country: 'DK',
          status: 'all',
          assetType: null,
          dateRange: 'all', // default due to invalid 'year'
        })
      })

      it('handles out-of-range minEvidence with valid other params', () => {
        const params = new URLSearchParams('min_evidence=10&status=active')
        const result = parseFilterParams(params)

        expect(result.minEvidence).toBe(1) // default
        expect(result.status).toBe('active')
      })
    })

    describe('URL key mapping', () => {
      it('uses snake_case URL param keys', () => {
        const params = new URLSearchParams()
        params.set(URL_PARAM_KEYS.minEvidence, '3')
        params.set(URL_PARAM_KEYS.dateRange, 'week')
        params.set(URL_PARAM_KEYS.assetType, 'military')

        const result = parseFilterParams(params)

        expect(result.minEvidence).toBe(3)
        expect(result.dateRange).toBe('week')
        expect(result.assetType).toBe('military')
      })

      it('ignores camelCase param keys', () => {
        const params = new URLSearchParams(
          'minEvidence=3&dateRange=week&assetType=military'
        )
        const result = parseFilterParams(params)

        // Should get defaults since snake_case keys are expected
        expect(result.minEvidence).toBe(DEFAULT_FILTER_STATE.minEvidence)
        expect(result.dateRange).toBe(DEFAULT_FILTER_STATE.dateRange)
        expect(result.assetType).toBe(DEFAULT_FILTER_STATE.assetType)
      })
    })

    describe('XSS/malicious URL params', () => {
      it('safely handles script injection in all params', () => {
        const params = new URLSearchParams(
          'min_evidence=<script>&country=<img+onerror>&status=javascript:&date_range=<body+onload>'
        )
        const result = parseFilterParams(params)

        // Invalid values should fall back to defaults
        expect(result.minEvidence).toBe(DEFAULT_FILTER_STATE.minEvidence)
        expect(result.dateRange).toBe(DEFAULT_FILTER_STATE.dateRange)
        // String values are returned as-is (XSS prevention at render layer)
        expect(result.country).toBe('<img onerror>')
        expect(result.status).toBe('javascript:')
      })
    })
  })

  describe('serializeFilterParams', () => {
    describe('full serialization', () => {
      it('serializes all non-default values', () => {
        const filters: FilterState = {
          minEvidence: 3,
          country: 'DK',
          status: 'active',
          assetType: 'airport',
          dateRange: 'week',
        }
        const params = serializeFilterParams(filters)

        expect(params.get('min_evidence')).toBe('3')
        expect(params.get('country')).toBe('DK')
        expect(params.get('status')).toBe('active')
        expect(params.get('asset_type')).toBe('airport')
        expect(params.get('date_range')).toBe('week')
      })

      it('produces correct URL string', () => {
        const filters: FilterState = {
          minEvidence: 2,
          country: 'SE',
          status: 'all',
          assetType: null,
          dateRange: 'month',
        }
        const params = serializeFilterParams(filters)
        const urlString = params.toString()

        expect(urlString).toContain('min_evidence=2')
        expect(urlString).toContain('country=SE')
        expect(urlString).toContain('date_range=month')
        expect(urlString).not.toContain('status=')
        expect(urlString).not.toContain('asset_type=')
      })
    })

    describe('default value handling', () => {
      it('omits all params when all values are defaults', () => {
        const params = serializeFilterParams(DEFAULT_FILTER_STATE)

        expect(params.toString()).toBe('')
      })

      it('omits default minEvidence (1)', () => {
        const filters: FilterState = {
          ...DEFAULT_FILTER_STATE,
          country: 'DK',
        }
        const params = serializeFilterParams(filters)

        expect(params.has('min_evidence')).toBe(false)
        expect(params.get('country')).toBe('DK')
      })

      it('omits default country ("all")', () => {
        const filters: FilterState = {
          ...DEFAULT_FILTER_STATE,
          minEvidence: 2,
        }
        const params = serializeFilterParams(filters)

        expect(params.has('country')).toBe(false)
        expect(params.get('min_evidence')).toBe('2')
      })

      it('omits default status ("all")', () => {
        const filters: FilterState = {
          ...DEFAULT_FILTER_STATE,
          dateRange: 'week',
        }
        const params = serializeFilterParams(filters)

        expect(params.has('status')).toBe(false)
        expect(params.get('date_range')).toBe('week')
      })

      it('omits null assetType', () => {
        const filters: FilterState = {
          ...DEFAULT_FILTER_STATE,
          country: 'NO',
        }
        const params = serializeFilterParams(filters)

        expect(params.has('asset_type')).toBe(false)
      })

      it('omits default dateRange ("all")', () => {
        const filters: FilterState = {
          ...DEFAULT_FILTER_STATE,
          status: 'resolved',
        }
        const params = serializeFilterParams(filters)

        expect(params.has('date_range')).toBe(false)
        expect(params.get('status')).toBe('resolved')
      })
    })

    describe('roundtrip consistency', () => {
      it('parse(serialize(filters)) equals original filters', () => {
        const original: FilterState = {
          minEvidence: 3,
          country: 'DK',
          status: 'active',
          assetType: 'airport',
          dateRange: 'week',
        }

        const serialized = serializeFilterParams(original)
        const parsed = parseFilterParams(serialized)

        expect(parsed).toEqual(original)
      })

      it('roundtrip works with partial non-default values', () => {
        const original: FilterState = {
          minEvidence: 2,
          country: 'all',
          status: 'all',
          assetType: null,
          dateRange: 'month',
        }

        const serialized = serializeFilterParams(original)
        const parsed = parseFilterParams(serialized)

        expect(parsed).toEqual(original)
      })

      it('roundtrip preserves default state', () => {
        const serialized = serializeFilterParams(DEFAULT_FILTER_STATE)
        const parsed = parseFilterParams(serialized)

        expect(parsed).toEqual(DEFAULT_FILTER_STATE)
      })
    })
  })

  describe('constants', () => {
    describe('DEFAULT_FILTER_STATE', () => {
      it('has all required FilterState properties', () => {
        expect(DEFAULT_FILTER_STATE).toHaveProperty('minEvidence')
        expect(DEFAULT_FILTER_STATE).toHaveProperty('country')
        expect(DEFAULT_FILTER_STATE).toHaveProperty('status')
        expect(DEFAULT_FILTER_STATE).toHaveProperty('assetType')
        expect(DEFAULT_FILTER_STATE).toHaveProperty('dateRange')
      })

      it('has correct default values', () => {
        expect(DEFAULT_FILTER_STATE.minEvidence).toBe(1)
        expect(DEFAULT_FILTER_STATE.country).toBe('all')
        expect(DEFAULT_FILTER_STATE.status).toBe('all')
        expect(DEFAULT_FILTER_STATE.assetType).toBeNull()
        expect(DEFAULT_FILTER_STATE.dateRange).toBe('all')
      })
    })

    describe('VALID_DATE_RANGES', () => {
      it('contains all valid date range values', () => {
        expect(VALID_DATE_RANGES).toContain('day')
        expect(VALID_DATE_RANGES).toContain('week')
        expect(VALID_DATE_RANGES).toContain('month')
        expect(VALID_DATE_RANGES).toContain('all')
      })

      it('has exactly 4 values', () => {
        expect(VALID_DATE_RANGES).toHaveLength(4)
      })
    })

    describe('MIN_EVIDENCE_RANGE', () => {
      it('has correct min and max values', () => {
        expect(MIN_EVIDENCE_RANGE.min).toBe(1)
        expect(MIN_EVIDENCE_RANGE.max).toBe(4)
      })
    })

    describe('URL_PARAM_KEYS', () => {
      it('uses snake_case for URL parameters', () => {
        expect(URL_PARAM_KEYS.minEvidence).toBe('min_evidence')
        expect(URL_PARAM_KEYS.dateRange).toBe('date_range')
        expect(URL_PARAM_KEYS.assetType).toBe('asset_type')
      })

      it('keeps simple keys unchanged', () => {
        expect(URL_PARAM_KEYS.country).toBe('country')
        expect(URL_PARAM_KEYS.status).toBe('status')
      })
    })
  })
})
