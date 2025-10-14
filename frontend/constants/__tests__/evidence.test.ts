import {
  EVIDENCE_SYSTEM,
  getEvidenceConfig,
  calculateEvidenceScore,
  type EvidenceScore,
} from '../evidence'

describe('Evidence System', () => {
  describe('EVIDENCE_SYSTEM constant', () => {
    it('contains all four evidence levels', () => {
      expect(EVIDENCE_SYSTEM[1]).toBeDefined()
      expect(EVIDENCE_SYSTEM[2]).toBeDefined()
      expect(EVIDENCE_SYSTEM[3]).toBeDefined()
      expect(EVIDENCE_SYSTEM[4]).toBeDefined()
    })

    it('has correct labels for each level', () => {
      expect(EVIDENCE_SYSTEM[4].label).toBe('OFFICIAL')
      expect(EVIDENCE_SYSTEM[3].label).toBe('VERIFIED')
      expect(EVIDENCE_SYSTEM[2].label).toBe('REPORTED')
      expect(EVIDENCE_SYSTEM[1].label).toBe('UNCONFIRMED')
    })

    it('has correct colors for each level', () => {
      expect(EVIDENCE_SYSTEM[4].color).toBe('#10b981') // emerald-500
      expect(EVIDENCE_SYSTEM[3].color).toBe('#f59e0b') // amber-500
      expect(EVIDENCE_SYSTEM[2].color).toBe('#f97316') // orange-500
      expect(EVIDENCE_SYSTEM[1].color).toBe('#ef4444') // red-500
    })

    it('has correct bgClass for each level', () => {
      expect(EVIDENCE_SYSTEM[4].bgClass).toBe('bg-emerald-500')
      expect(EVIDENCE_SYSTEM[3].bgClass).toBe('bg-amber-500')
      expect(EVIDENCE_SYSTEM[2].bgClass).toBe('bg-orange-500')
      expect(EVIDENCE_SYSTEM[1].bgClass).toBe('bg-red-500')
    })

    it('has gradient definitions for all levels', () => {
      expect(EVIDENCE_SYSTEM[1].gradient).toContain('linear-gradient')
      expect(EVIDENCE_SYSTEM[2].gradient).toContain('linear-gradient')
      expect(EVIDENCE_SYSTEM[3].gradient).toContain('linear-gradient')
      expect(EVIDENCE_SYSTEM[4].gradient).toContain('linear-gradient')
    })

    it('has emoji for all levels', () => {
      expect(EVIDENCE_SYSTEM[4].emoji).toBe('🟢')
      expect(EVIDENCE_SYSTEM[3].emoji).toBe('🟡')
      expect(EVIDENCE_SYSTEM[2].emoji).toBe('🟠')
      expect(EVIDENCE_SYSTEM[1].emoji).toBe('🔴')
    })

    it('has descriptions for all levels', () => {
      expect(EVIDENCE_SYSTEM[4].description).toContain('official')
      expect(EVIDENCE_SYSTEM[3].description).toContain('Multiple credible')
      expect(EVIDENCE_SYSTEM[2].description).toContain('Single credible')
      expect(EVIDENCE_SYSTEM[1].description).toContain('Social media')
    })

    it('has correct requiresOfficial flags', () => {
      expect(EVIDENCE_SYSTEM[4].requiresOfficial).toBe(true)
      expect(EVIDENCE_SYSTEM[3].requiresOfficial).toBe(false)
      expect(EVIDENCE_SYSTEM[2].requiresOfficial).toBe(false)
      expect(EVIDENCE_SYSTEM[1].requiresOfficial).toBe(false)
    })
  })

  describe('getEvidenceConfig', () => {
    it('returns correct config for score 4', () => {
      const config = getEvidenceConfig(4)
      expect(config.label).toBe('OFFICIAL')
      expect(config.color).toBe('#10b981')
    })

    it('returns correct config for score 3', () => {
      const config = getEvidenceConfig(3)
      expect(config.label).toBe('VERIFIED')
      expect(config.color).toBe('#f59e0b')
    })

    it('returns correct config for score 2', () => {
      const config = getEvidenceConfig(2)
      expect(config.label).toBe('REPORTED')
      expect(config.color).toBe('#f97316')
    })

    it('returns correct config for score 1', () => {
      const config = getEvidenceConfig(1)
      expect(config.label).toBe('UNCONFIRMED')
      expect(config.color).toBe('#ef4444')
    })

    it('returns config with all required properties', () => {
      const config = getEvidenceConfig(4)
      expect(config).toHaveProperty('label')
      expect(config).toHaveProperty('shortLabel')
      expect(config).toHaveProperty('color')
      expect(config).toHaveProperty('colorDark')
      expect(config).toHaveProperty('bgClass')
      expect(config).toHaveProperty('textClass')
      expect(config).toHaveProperty('borderClass')
      expect(config).toHaveProperty('gradient')
      expect(config).toHaveProperty('glow')
      expect(config).toHaveProperty('icon')
      expect(config).toHaveProperty('description')
      expect(config).toHaveProperty('emoji')
      expect(config).toHaveProperty('minSources')
      expect(config).toHaveProperty('requiresOfficial')
    })
  })

  describe('calculateEvidenceScore', () => {
    it('returns 1 for empty sources array', () => {
      const score = calculateEvidenceScore([])
      expect(score).toBe(1)
    })

    it('returns 4 for police source', () => {
      const sources = [{ source_type: 'police' }]
      const score = calculateEvidenceScore(sources)
      expect(score).toBe(4)
    })

    it('returns 4 for military source', () => {
      const sources = [{ source_type: 'military' }]
      const score = calculateEvidenceScore(sources)
      expect(score).toBe(4)
    })

    it('returns 4 for NOTAM source', () => {
      const sources = [{ source_type: 'notam' }]
      const score = calculateEvidenceScore(sources)
      expect(score).toBe(4)
    })

    it('returns 4 for aviation authority source', () => {
      const sources = [{ source_type: 'aviation' }]
      const score = calculateEvidenceScore(sources)
      expect(score).toBe(4)
    })

    it('returns 4 if any source is official', () => {
      const sources = [
        { source_type: 'news' },
        { source_type: 'police' },
        { source_type: 'twitter' },
      ]
      const score = calculateEvidenceScore(sources)
      expect(score).toBe(4)
    })

    it('returns 3 for 2 non-official sources', () => {
      const sources = [{ source_type: 'news' }, { source_type: 'media' }]
      const score = calculateEvidenceScore(sources)
      expect(score).toBe(3)
    })

    it('returns 3 for 3+ non-official sources', () => {
      const sources = [
        { source_type: 'news' },
        { source_type: 'media' },
        { source_type: 'press' },
      ]
      const score = calculateEvidenceScore(sources)
      expect(score).toBe(3)
    })

    it('returns 2 for single non-official source', () => {
      const sources = [{ source_type: 'news' }]
      const score = calculateEvidenceScore(sources)
      expect(score).toBe(2)
    })

    it('handles case-insensitive source types', () => {
      const sources = [{ source_type: 'POLICE' }]
      const score = calculateEvidenceScore(sources)
      expect(score).toBe(4)
    })

    it('handles mixed case source types', () => {
      const sources = [{ source_type: 'Police' }]
      const score = calculateEvidenceScore(sources)
      expect(score).toBe(4)
    })
  })

  describe('Evidence system consistency', () => {
    it('all levels have consistent property structure', () => {
      const scores: EvidenceScore[] = [1, 2, 3, 4]
      const requiredProps = [
        'label',
        'shortLabel',
        'color',
        'colorDark',
        'bgClass',
        'textClass',
        'borderClass',
        'gradient',
        'glow',
        'icon',
        'description',
        'emoji',
        'minSources',
        'requiresOfficial',
      ]

      scores.forEach((score) => {
        const config = EVIDENCE_SYSTEM[score]
        requiredProps.forEach((prop) => {
          expect(config).toHaveProperty(prop)
        })
      })
    })

    it('colors follow severity order (red > orange > amber > green)', () => {
      // Lower scores should have warmer/more urgent colors
      expect(EVIDENCE_SYSTEM[1].color).toBe('#ef4444') // red
      expect(EVIDENCE_SYSTEM[2].color).toBe('#f97316') // orange
      expect(EVIDENCE_SYSTEM[3].color).toBe('#f59e0b') // amber
      expect(EVIDENCE_SYSTEM[4].color).toBe('#10b981') // green
    })

    it('minSources increases with evidence level', () => {
      expect(EVIDENCE_SYSTEM[1].minSources).toBe(0)
      expect(EVIDENCE_SYSTEM[2].minSources).toBe(1)
      expect(EVIDENCE_SYSTEM[3].minSources).toBe(2)
      expect(EVIDENCE_SYSTEM[4].minSources).toBe(1) // Only 1 needed if official
    })
  })
})
