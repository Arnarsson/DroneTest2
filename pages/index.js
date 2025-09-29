import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import Head from 'next/head';

// Load map component only on client side
const Map = dynamic(() => import('../components/Map'), { ssr: false });

export default function Home() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    minEvidence: 2,
    country: 'DK',
    status: 'active'
  });

  useEffect(() => {
    fetchIncidents();
  }, [filters]);

  const fetchIncidents = async () => {
    try {
      setLoading(true);

      // Build query params
      const params = new URLSearchParams({
        min_evidence: filters.minEvidence,
        country: filters.country,
        status: filters.status,
        limit: 500
      });

      // Fetch from your live API
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
      const response = await fetch(`${apiUrl}/incidents?${params}`);

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      setIncidents(data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch incidents:', err);
      setError(err.message);

      // Fallback to demo data if API fails
      setIncidents([
        {
          id: '1',
          title: 'Demo: Drone at Copenhagen Airport',
          lat: 55.6180,
          lon: 12.6476,
          evidence_score: 3,
          occurred_at: new Date().toISOString(),
          narrative: 'This is demo data - API connection pending'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>DroneWatch - Live Drone Incident Tracking</title>
        <meta name="description" content="Real-time tracking of drone incidents across the Nordics" />
      </Head>

      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">🚁 DroneWatch</h1>
              <span className="ml-4 text-sm text-gray-500">
                Live tracking of drone incidents
              </span>
            </div>

            {/* Status indicator */}
            <div className="flex items-center space-x-2">
              <div className={`h-3 w-3 rounded-full ${error ? 'bg-red-500' : 'bg-green-500'} animate-pulse`}></div>
              <span className="text-sm text-gray-600">
                {loading ? 'Loading...' : `${incidents.length} incidents`}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Filters */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex flex-wrap gap-4">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Evidence Level</label>
              <select
                className="border rounded px-3 py-1 text-sm"
                value={filters.minEvidence}
                onChange={(e) => setFilters({...filters, minEvidence: e.target.value})}
              >
                <option value="1">All</option>
                <option value="2">OSINT+ (≥2)</option>
                <option value="3">Verified (≥3)</option>
                <option value="4">Official Only (4)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs text-gray-500 mb-1">Country</label>
              <select
                className="border rounded px-3 py-1 text-sm"
                value={filters.country}
                onChange={(e) => setFilters({...filters, country: e.target.value})}
              >
                <option value="DK">Denmark</option>
                <option value="NO">Norway</option>
                <option value="SE">Sweden</option>
                <option value="FI">Finland</option>
              </select>
            </div>

            <div>
              <label className="block text-xs text-gray-500 mb-1">Status</label>
              <select
                className="border rounded px-3 py-1 text-sm"
                value={filters.status}
                onChange={(e) => setFilters({...filters, status: e.target.value})}
              >
                <option value="active">Active</option>
                <option value="resolved">Resolved</option>
                <option value="unconfirmed">Unconfirmed</option>
              </select>
            </div>

            <button
              onClick={fetchIncidents}
              className="px-4 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
          <div className="flex">
            <div className="ml-3">
              <p className="text-sm text-yellow-700">
                API Connection Issue: {error}. Showing demo data.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Map */}
      <main className="flex-1">
        <Map incidents={incidents} loading={loading} />
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-4">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm">
          <p>DroneWatch © 2025 | Data sources: Police, Media, NOTAMs</p>
          <p className="mt-1 text-gray-400">
            API: {process.env.NEXT_PUBLIC_API_URL || 'Not configured'}
          </p>
        </div>
      </footer>
    </div>
  );
}