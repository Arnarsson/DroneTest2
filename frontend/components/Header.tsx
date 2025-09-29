export function Header({ incidentCount, isLoading }: {
  incidentCount: number
  isLoading: boolean
}) {
  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <span className="text-3xl">🚁</span>
              DroneWatch
            </h1>
            <span className="ml-4 text-sm text-gray-500">
              Real-time drone incident tracking
            </span>
          </div>

          <div className="flex items-center gap-4">
            {/* Live indicator */}
            <div className="flex items-center gap-2">
              <div className={`h-3 w-3 rounded-full ${isLoading ? 'bg-yellow-400' : 'bg-green-500'} animate-pulse`} />
              <span className="text-sm font-medium text-gray-700">
                {isLoading ? 'Updating...' : `${incidentCount} incidents`}
              </span>
            </div>

            {/* Info button */}
            <button
              onClick={() => window.open('/about', '_blank')}
              className="text-gray-500 hover:text-gray-700 p-2"
              title="About DroneWatch"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}