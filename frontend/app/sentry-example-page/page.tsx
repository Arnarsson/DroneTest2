'use client'

import * as Sentry from '@sentry/nextjs'

export default function SentryExamplePage() {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      padding: '2rem',
      fontFamily: 'system-ui, sans-serif'
    }}>
      <h1 style={{ marginBottom: '2rem' }}>Sentry Example Page</h1>
      <p style={{ marginBottom: '2rem', color: '#666' }}>
        Click the button below to throw a test error and verify Sentry integration
      </p>
      <button
        type="button"
        onClick={() => {
          throw new Error('Sentry Test Error - Integration Verified!')
        }}
        style={{
          padding: '1rem 2rem',
          fontSize: '1.2rem',
          backgroundColor: '#e74c3c',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: 'pointer',
          fontWeight: 'bold',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
          transition: 'all 0.2s'
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.transform = 'scale(1.05)'
          e.currentTarget.style.boxShadow = '0 6px 12px rgba(0,0,0,0.15)'
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.transform = 'scale(1)'
          e.currentTarget.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)'
        }}
      >
        🚨 Trigger Test Error
      </button>
      <div style={{
        marginTop: '3rem',
        padding: '1.5rem',
        backgroundColor: '#f8f9fa',
        borderRadius: '8px',
        maxWidth: '600px',
        textAlign: 'center'
      }}>
        <h3 style={{ marginBottom: '1rem' }}>What happens when you click?</h3>
        <ol style={{ textAlign: 'left', lineHeight: '1.8' }}>
          <li>A JavaScript error will be thrown</li>
          <li>Sentry will capture the error automatically</li>
          <li>The error will appear in your Sentry dashboard</li>
          <li>You can verify the integration is working</li>
        </ol>
        <p style={{ marginTop: '1.5rem', color: '#888', fontSize: '0.9rem' }}>
          After clicking, check your Sentry Issues tab to see the captured error
        </p>
      </div>
    </div>
  )
}
