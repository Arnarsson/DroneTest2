export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16">
            <a href="/" className="text-2xl font-bold text-gray-900 flex items-center gap-2 hover:text-gray-700">
              <span className="text-3xl">🚁</span>
              DroneWatch
            </a>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">About DroneWatch</h1>
          <p className="text-lg text-gray-600 mb-6">
            Real-time tracking and analysis of drone incidents across Europe, powered by evidence-based reporting.
          </p>
          <div className="border-t border-gray-200 pt-6">
            <p className="text-gray-700 leading-relaxed">
              DroneWatch aggregates verified drone incidents from police reports, aviation authorities,
              and trusted news sources. Our mission is to provide security researchers, journalists,
              and aviation professionals with reliable, factual data on unauthorized drone activity.
            </p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Evidence Scoring System</h2>
          <p className="text-gray-600 mb-6">
            Each incident is rated on a 1-4 scale based on source reliability and verification:
          </p>

          <div className="space-y-6">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-12 h-12 bg-gray-500 rounded-full flex items-center justify-center text-white font-bold text-xl">
                1
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Unverified / Social Media</h3>
                <p className="text-gray-600 mt-1">
                  Initial reports from social media, local witnesses, or single unconfirmed sources.
                  Treated as rumor until independently verified.
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  <strong>Sources:</strong> Twitter/X posts, Facebook reports, forum discussions
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-12 h-12 bg-yellow-500 rounded-full flex items-center justify-center text-white font-bold text-xl">
                2
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">OSINT / News Reports</h3>
                <p className="text-gray-600 mt-1">
                  Verified by multiple independent news sources or open-source intelligence.
                  Cross-referenced but not officially confirmed.
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  <strong>Sources:</strong> Multiple news outlets, aviation tracking sites, OSINT researchers
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-12 h-12 bg-orange-500 rounded-full flex items-center justify-center text-white font-bold text-xl">
                3
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Verified Media / Official Statement</h3>
                <p className="text-gray-600 mt-1">
                  Confirmed by police statements, aviation authority notices, or established media
                  with direct official sources.
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  <strong>Sources:</strong> Police press releases, NOTAM alerts, major news with official quotes
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-12 h-12 bg-red-600 rounded-full flex items-center justify-center text-white font-bold text-xl">
                4
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Official Report</h3>
                <p className="text-gray-600 mt-1">
                  Published incident reports from police, military, aviation authorities, or government
                  agencies with full details and documentation.
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  <strong>Sources:</strong> Official investigation reports, government press conferences, aviation incident databases
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Data Sources</h2>
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">🚓 Police Feeds</h3>
              <p className="text-gray-600 mt-1">
                Official RSS feeds from Danish police, Norwegian police, Swedish police
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">✈️ Aviation Authorities</h3>
              <p className="text-gray-600 mt-1">
                NOTAM notices, airport incident reports, air traffic control communications
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">📰 News Media</h3>
              <p className="text-gray-600 mt-1">
                Google News alerts, regional newspapers, aviation press
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">👁️ OSINT Community</h3>
              <p className="text-gray-600 mt-1">
                Verified reports from open-source intelligence researchers and analysts
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">How to Use the Map</h2>
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">🗺️ Map View</h3>
              <p className="text-gray-600 mt-1">
                Click on markers to see incident details. Clusters (numbered circles) show multiple
                incidents in the same area - click to zoom in and separate them.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">🔍 Filters</h3>
              <p className="text-gray-600 mt-1">
                Use the filter bar to narrow results by evidence level, country, status, location type,
                and time period. Filters update the map in real-time.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">📋 List View</h3>
              <p className="text-gray-600 mt-1">
                Switch to list view for a detailed table of all filtered incidents with sortable columns
                and quick access to sources.
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Technology</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">Frontend</h3>
              <ul className="text-gray-700 space-y-1">
                <li>• Next.js 14 + React</li>
                <li>• TypeScript + Tailwind CSS</li>
                <li>• Leaflet.js maps</li>
              </ul>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">Backend</h3>
              <ul className="text-gray-700 space-y-1">
                <li>• Vercel Serverless Functions</li>
                <li>• Supabase (PostgreSQL + PostGIS)</li>
                <li>• GitHub Actions scraper</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Contact & Contributing</h2>
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Report an Incident</h3>
              <p className="text-gray-600 mt-1">
                Have information about a drone incident? Email us at{' '}
                <a href="mailto:report@dronemap.cc" className="text-blue-600 hover:text-blue-800">
                  report@dronemap.cc
                </a>{' '}
                with the date, location, and source links.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Open Source</h3>
              <p className="text-gray-600 mt-1">
                DroneWatch is open source. Contribute on{' '}
                <a
                  href="https://github.com/Arnarsson/2"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800"
                >
                  GitHub
                </a>
                .
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Privacy & Data Use</h3>
              <p className="text-gray-600 mt-1">
                All incident data is from public sources. We do not collect personal information.
                The dataset is available for academic research and journalism.
              </p>
            </div>
          </div>
        </div>

        <div className="text-center mt-12 pb-8">
          <a
            href="/"
            className="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium"
          >
            ← Back to Map
          </a>
        </div>
      </main>
    </div>
  )
}