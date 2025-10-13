'use client'

import { useEffect } from 'react'
import * as Sentry from '@sentry/nextjs'

export default function TestSentry() {
  useEffect(() => {
    // Send a test message
    Sentry.captureMessage('Sentry test page loaded', {
      level: 'info',
      tags: {
        test: 'true',
        page: 'test-sentry'
      }
    })

    // Test error capture
    try {
      throw new Error('Test error from Sentry test page')
    } catch (error) {
      Sentry.captureException(error)
    }

    // Test breadcrumbs
    Sentry.addBreadcrumb({
      category: 'test',
      message: 'Test breadcrumb added',
      level: 'info',
    })
  }, [])

  const handleTestError = () => {
    throw new Error('Manual test error triggered by button click')
  }

  const handleTestMessage = () => {
    Sentry.captureMessage('Manual test message from button', {
      level: 'warning',
      extra: {
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent
      }
    })
    alert('Test message sent to Sentry!')
  }

  return (
    <div style={{ padding: '2rem', fontFamily: 'monospace' }}>
      <h1>🧪 Sentry Test Page</h1>
      <p>This page sends test events to Sentry to verify integration.</p>

      <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem', flexDirection: 'column', maxWidth: '400px' }}>
        <button
          onClick={handleTestMessage}
          style={{
            padding: '1rem',
            backgroundColor: '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          📤 Send Test Message
        </button>

        <button
          onClick={handleTestError}
          style={{
            padding: '1rem',
            backgroundColor: '#f44336',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          💥 Trigger Test Error
        </button>
      </div>

      <div style={{ marginTop: '2rem', padding: '1rem', backgroundColor: '#f0f0f0', borderRadius: '4px' }}>
        <h3>✅ Events Sent on Page Load:</h3>
        <ul>
          <li>Info message: "Sentry test page loaded"</li>
          <li>Test error captured</li>
          <li>Breadcrumb added</li>
        </ul>

        <h3 style={{ marginTop: '1rem' }}>🔍 Check Sentry Dashboard:</h3>
        <p>Go to: <a href="https://sentry.io/organizations/svc-cc/projects/dronewatch/" target="_blank">Sentry Dashboard</a></p>
        <p>Look in the <strong>Issues</strong> tab for the test events.</p>
      </div>

      <div style={{ marginTop: '2rem', padding: '1rem', backgroundColor: '#fff3cd', borderRadius: '4px' }}>
        <h3>⚠️ Note:</h3>
        <p>This is a test page. Events sent from here are for testing Sentry integration only.</p>
        <p>After confirming Sentry works, visit the main site to capture real data.</p>
      </div>
    </div>
  )
}
