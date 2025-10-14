import { ENV } from '../env'

describe('ENV Configuration', () => {
  const originalEnv = process.env

  beforeEach(() => {
    jest.resetModules()
    process.env = { ...originalEnv }
  })

  afterEach(() => {
    process.env = originalEnv
  })

  describe('API_URL configuration', () => {
    it('uses NEXT_PUBLIC_API_URL when set', () => {
      process.env.NEXT_PUBLIC_API_URL = 'https://custom-api.example.com/api'
      jest.resetModules()
      const { ENV: testEnv } = require('../env')

      expect(testEnv.API_URL).toBe('https://custom-api.example.com/api')
    })

    it('uses localhost in development when NEXT_PUBLIC_API_URL not set', () => {
      delete process.env.NEXT_PUBLIC_API_URL
      process.env.NODE_ENV = 'development'
      jest.resetModules()
      const { ENV: testEnv } = require('../env')

      expect(testEnv.API_URL).toBe('http://localhost:3000/api')
    })

    it('uses production fallback when not in development and no NEXT_PUBLIC_API_URL', () => {
      delete process.env.NEXT_PUBLIC_API_URL
      process.env.NODE_ENV = 'production'
      jest.resetModules()
      const { ENV: testEnv } = require('../env')

      expect(testEnv.API_URL).toBe('https://www.dronemap.cc/api')
    })
  })

  describe('NODE_ENV configuration', () => {
    it('uses NODE_ENV when set', () => {
      process.env.NODE_ENV = 'production'
      jest.resetModules()
      const { ENV: testEnv } = require('../env')

      expect(testEnv.NODE_ENV).toBe('production')
    })

    it('defaults to development when NODE_ENV not set', () => {
      delete process.env.NODE_ENV
      jest.resetModules()
      const { ENV: testEnv } = require('../env')

      expect(testEnv.NODE_ENV).toBe('development')
    })

    it('recognizes test environment', () => {
      process.env.NODE_ENV = 'test'
      jest.resetModules()
      const { ENV: testEnv } = require('../env')

      expect(testEnv.NODE_ENV).toBe('test')
    })
  })

  describe('ENV object', () => {
    it('has all required properties', () => {
      expect(ENV).toHaveProperty('API_URL')
      expect(ENV).toHaveProperty('NODE_ENV')
    })

    it('exports as default', () => {
      const defaultExport = require('../env').default
      expect(defaultExport).toStrictEqual(ENV)
    })

    it('has string values for all properties', () => {
      expect(typeof ENV.API_URL).toBe('string')
      expect(typeof ENV.NODE_ENV).toBe('string')
    })
  })

  describe('environment validation', () => {
    it('has correct API URL format for production', () => {
      delete process.env.NEXT_PUBLIC_API_URL
      process.env.NODE_ENV = 'production'
      jest.resetModules()
      const { ENV: testEnv } = require('../env')

      expect(testEnv.API_URL).toMatch(/^https:\/\//)
      expect(testEnv.API_URL).toContain('/api')
    })

    it('has correct API URL format for development', () => {
      delete process.env.NEXT_PUBLIC_API_URL
      process.env.NODE_ENV = 'development'
      jest.resetModules()
      const { ENV: testEnv } = require('../env')

      expect(testEnv.API_URL).toMatch(/^http:\/\/localhost/)
      expect(testEnv.API_URL).toContain('/api')
    })
  })
})
