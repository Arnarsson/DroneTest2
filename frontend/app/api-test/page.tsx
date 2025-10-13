'use client'

import { useEffect, useState } from 'react'

export default function ApiTest() {
  const [result, setResult] = useState('Loading...')
  const [testTime, setTestTime] = useState('')

  useEffect(() => {
    const startTime = Date.now()
    setTestTime(new Date().toISOString())

    console.log('🧪 API Test starting:', 'https://www.dronemap.cc/api/incidents')

    fetch('https://www.dronemap.cc/api/incidents', {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    })
      .then(response => {
        const elapsed = Date.now() - startTime
        console.log('✅ Response received:', response.status, `(${elapsed}ms)`)
        console.log('📋 Headers:', Object.fromEntries(response.headers.entries()))
        return response.json()
      })
      .then(data => {
        const elapsed = Date.now() - startTime
        console.log('✅ Data parsed:', data.length, 'incidents', `(${elapsed}ms)`)
        setResult(JSON.stringify({
          success: true,
          count: data.length,
          elapsed_ms: elapsed,
          sample: data[0],
          all: data
        }, null, 2))
      })
      .catch(error => {
        const elapsed = Date.now() - startTime
        console.error('❌ Error:', error, `(${elapsed}ms)`)
        setResult(JSON.stringify({
          success: false,
          error: error.message,
          elapsed_ms: elapsed,
          stack: error.stack
        }, null, 2))
      })
  }, [])

  return (
    <div style={{ padding: '2rem', fontFamily: 'monospace', backgroundColor: '#1a1a1a', color: '#00ff00', minHeight: '100vh' }}>
      <h1 style={{ color: '#00ff00', marginBottom: '1rem' }}>🧪 DroneWatch API Diagnostic Test</h1>
      <div style={{ marginBottom: '1rem', color: '#ffff00' }}>
        <strong>Test Time:</strong> {testTime}
      </div>
      <div style={{ marginBottom: '1rem', color: '#ffff00' }}>
        <strong>API URL:</strong> https://www.dronemap.cc/api/incidents
      </div>
      <div style={{ backgroundColor: '#000', padding: '1rem', borderRadius: '4px', overflow: 'auto' }}>
        <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>{result}</pre>
      </div>
      <div style={{ marginTop: '2rem', color: '#888' }}>
        <p>This is a simple diagnostic page that bypasses React Query and useIncidents hook.</p>
        <p>It makes a direct fetch() call to test API connectivity from the browser.</p>
        <p>Open browser DevTools (F12) to see detailed console logs.</p>
      </div>
    </div>
  )
}
