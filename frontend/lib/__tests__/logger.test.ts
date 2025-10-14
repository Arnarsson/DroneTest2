import { logger } from '../logger'

describe('Logger', () => {
  const originalEnv = process.env.NODE_ENV
  let consoleLogSpy: jest.SpyInstance
  let consoleDebugSpy: jest.SpyInstance
  let consoleWarnSpy: jest.SpyInstance
  let consoleErrorSpy: jest.SpyInstance

  beforeEach(() => {
    consoleLogSpy = jest.spyOn(console, 'log').mockImplementation()
    consoleDebugSpy = jest.spyOn(console, 'debug').mockImplementation()
    consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation()
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation()
  })

  afterEach(() => {
    consoleLogSpy.mockRestore()
    consoleDebugSpy.mockRestore()
    consoleWarnSpy.mockRestore()
    consoleErrorSpy.mockRestore()
    process.env.NODE_ENV = originalEnv
  })

  describe('in development environment', () => {
    beforeEach(() => {
      process.env.NODE_ENV = 'development'
    })

    it('logs messages with prefix in development', () => {
      // Need to re-import to pick up new NODE_ENV
      jest.resetModules()
      const { logger: devLogger } = require('../logger')

      devLogger.log('test message')
      expect(consoleLogSpy).toHaveBeenCalledWith('[DroneWatch]', 'test message')
    })

    it('logs debug messages in development', () => {
      jest.resetModules()
      const { logger: devLogger } = require('../logger')

      devLogger.debug('debug info')
      expect(consoleDebugSpy).toHaveBeenCalledWith('[DroneWatch]', 'debug info')
    })

    it('logs warnings in development', () => {
      jest.resetModules()
      const { logger: devLogger } = require('../logger')

      devLogger.warn('warning message')
      expect(consoleWarnSpy).toHaveBeenCalledWith('[DroneWatch]', 'warning message')
    })

    it('logs errors in development', () => {
      jest.resetModules()
      const { logger: devLogger } = require('../logger')

      devLogger.error('error message')
      expect(consoleErrorSpy).toHaveBeenCalledWith('[DroneWatch]', 'error message')
    })

    it('handles multiple arguments', () => {
      jest.resetModules()
      const { logger: devLogger } = require('../logger')

      devLogger.log('message', 123, { key: 'value' })
      expect(consoleLogSpy).toHaveBeenCalledWith(
        '[DroneWatch]',
        'message',
        123,
        { key: 'value' }
      )
    })
  })

  describe('in production environment', () => {
    beforeEach(() => {
      process.env.NODE_ENV = 'production'
    })

    it('does not log regular messages in production', () => {
      jest.resetModules()
      const { logger: prodLogger } = require('../logger')

      prodLogger.log('test message')
      expect(consoleLogSpy).not.toHaveBeenCalled()
    })

    it('does not log debug messages in production', () => {
      jest.resetModules()
      const { logger: prodLogger } = require('../logger')

      prodLogger.debug('debug info')
      expect(consoleDebugSpy).not.toHaveBeenCalled()
    })

    it('does not log warnings in production', () => {
      jest.resetModules()
      const { logger: prodLogger } = require('../logger')

      prodLogger.warn('warning message')
      expect(consoleWarnSpy).not.toHaveBeenCalled()
    })

    it('always logs errors even in production', () => {
      jest.resetModules()
      const { logger: prodLogger } = require('../logger')

      prodLogger.error('error message')
      expect(consoleErrorSpy).toHaveBeenCalledWith('[DroneWatch]', 'error message')
    })

    it('logs error objects in production', () => {
      jest.resetModules()
      const { logger: prodLogger } = require('../logger')

      const error = new Error('test error')
      prodLogger.error('Error occurred:', error)
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[DroneWatch]',
        'Error occurred:',
        error
      )
    })
  })

  describe('logger methods', () => {
    it('has all required methods', () => {
      expect(logger).toHaveProperty('log')
      expect(logger).toHaveProperty('debug')
      expect(logger).toHaveProperty('warn')
      expect(logger).toHaveProperty('error')
    })

    it('all methods are functions', () => {
      expect(typeof logger.log).toBe('function')
      expect(typeof logger.debug).toBe('function')
      expect(typeof logger.warn).toBe('function')
      expect(typeof logger.error).toBe('function')
    })
  })
})
