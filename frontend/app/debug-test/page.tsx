'use client'

import { useEffect, useState } from 'react'
import { ENV } from '@/lib/env'

export default function DebugTest() {
  const [logs, setLogs] = useState<string[]>([])
  const [incidents, setIncidents] = useState<any[]>([])

  const log = (msg: string) => {
    const timestamp = new Date().toISOString().split('T')[1]
    setLogs(prev => [...prev, `[${timestamp}] ${msg}`])
    console.log(msg)
  }

  useEffect(() => {
    log('🚀 Component mounted')
    log(`📍 ENV.API_URL = "${ENV.API_URL}"`)
    log(`📍 process.env.NEXT_PUBLIC_API_URL = "${process.env.NEXT_PUBLIC_API_URL}"`)
    log(`📍 NODE_ENV = "${process.env.NODE_ENV}"`)

    const testAPI = async () => {
      try {
        const url = `${ENV.API_URL}/incidents`
        log(`🔗 Fetching from: ${url}`)

        const startTime = Date.now()
        const response = await fetch(url)
        const elapsed = Date.now() - startTime

        log(`✅ Response received (${elapsed}ms)`)
        log(`📊 Status: ${response.status} ${response.statusText}`)
        log(`📋 CORS header: ${response.headers.get('access-control-allow-origin')}`)

        const data = await response.json()
        log(`📦 Incidents received: ${data.length}`)

        setIncidents(data)

        if (data.length > 0) {
          log(`✅ SUCCESS: ${data.length} incidents loaded`)
        } else {
          log(`⚠️ WARNING: API returned empty array`)
        }
      } catch (error: any) {
        log(`❌ ERROR: ${error.message}`)
        log(`📚 Stack: ${error.stack}`)
      }
    }

    testAPI()
  }, [])

  return (
    <div style={{
      padding: '20px',
      fontFamily: 'monospace',
      backgroundColor: '#000',
      color: '#0f0',
      minHeight: '100vh'
    }}>
      <h1 style={{ color: '#0ff', marginBottom: '20px' }}>
        🐛 DroneWatch Debug Test
      </h1>

      <div style={{ marginBottom: '30px', backgroundColor: '#111', padding: '15px', borderRadius: '5px' }}>
        <h2 style={{ color: '#ff0', marginBottom: '10px' }}>📋 Console Logs:</h2>
        <div style={{ maxHeight: '300px', overflow: 'auto' }}>
          {logs.map((log, i) => (
            <div key={i} style={{ marginBottom: '5px', fontSize: '14px' }}>{log}</div>
          ))}
        </div>
      </div>

      <div style={{ backgroundColor: '#111', padding: '15px', borderRadius: '5px' }}>
        <h2 style={{ color: '#ff0', marginBottom: '10px' }}>
          📊 Incidents ({incidents.length}):
        </h2>
        {incidents.length === 0 ? (
          <div style={{ color: '#f00' }}>No incidents loaded</div>
        ) : (
          <div style={{ maxHeight: '400px', overflow: 'auto' }}>
            {incidents.slice(0, 3).map((incident, i) => (
              <div key={i} style={{
                marginBottom: '15px',
                padding: '10px',
                backgroundColor: '#222',
                borderLeft: '3px solid #0f0'
              }}>
                <div><strong>Title:</strong> {incident.title}</div>
                <div><strong>Date:</strong> {incident.incident_date}</div>
                <div><strong>Location:</strong> {incident.country}</div>
                <div><strong>Evidence:</strong> {incident.evidence_score}</div>
              </div>
            ))}
            {incidents.length > 3 && (
              <div style={{ color: '#888', marginTop: '10px' }}>
                ... and {incidents.length - 3} more
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
