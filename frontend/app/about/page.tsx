"use client";

import { DroneWatchLogo } from "@/components/DroneWatchLogo";
import { EvidenceBadge } from "@/components/EvidenceBadge";
import { motion } from "framer-motion";
import Link from "next/link";

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-gray-100 to-gray-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 transition-colors">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/95 dark:bg-gray-900/95 backdrop-blur-2xl border-b border-gray-200/70 dark:border-gray-800/70 shadow-sm transition-all">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link
              href="/"
              className="flex items-center gap-3 text-gray-900 dark:text-white hover:opacity-80 transition-opacity"
            >
              <DroneWatchLogo size="md" />
              <span className="text-xl font-bold tracking-tight">
                DroneWatch
              </span>
            </Link>
            <Link
              href="/"
              className="text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              Back to Map →
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-white mb-4 tracking-tight">
            DroneWatch
          </h1>
          <p className="text-xl sm:text-2xl text-gray-600 dark:text-gray-300 font-medium max-w-3xl mx-auto">
            Safety Through Transparency
          </p>
          <div className="mt-6 flex items-center justify-center gap-4 text-sm text-gray-500 dark:text-gray-400">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>Live Data</span>
            </div>
            <span>•</span>
            <div className="flex items-center gap-2">
              <span>Open Source</span>
            </div>
          </div>
        </motion.div>

        {/* Mission Statement */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="mb-12 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-200/70 dark:border-gray-800/70 p-8 shadow-soft"
        >
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center">
              <svg
                className="w-6 h-6 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                />
              </svg>
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                About
              </h2>
              <p className="text-gray-700 dark:text-gray-300 leading-relaxed mb-4">
                DroneWatch provides real-time, evidence-based tracking of
                unauthorized drone incidents across Europe. We serve security
                researchers, aviation professionals, journalists, and policy
                makers who need reliable, verifiable data on drone-related
                events.
              </p>
              <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                By aggregating data from official sources—police reports,
                aviation authorities, and verified media—we enable informed
                decision-making without speculation or sensationalism. Every
                incident is scored, sourced, and traceable.
              </p>
            </div>
          </div>
        </motion.section>

        {/* Evidence Scoring Methodology */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mb-12"
        >
          <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-200/70 dark:border-gray-800/70 p-8 shadow-soft">
            <div className="flex items-center gap-3 mb-6">
              <div className="flex-shrink-0 w-12 h-12 bg-emerald-600 rounded-xl flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Evidence Scoring System
              </h2>
            </div>

            <p className="text-gray-600 dark:text-gray-400 mb-8">
              We use a 4-tier scoring system based on source reliability and
              verification. Each incident receives a score from 1 (unconfirmed)
              to 4 (officially verified).
            </p>

            <div className="space-y-6">
              {/* Score 4 - Official */}
              <div className="group p-6 rounded-xl bg-gradient-to-r from-emerald-50 to-transparent dark:from-emerald-950/20 dark:to-transparent border border-emerald-200 dark:border-emerald-800/30 hover:shadow-md transition-all">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <EvidenceBadge score={4} showTooltip={false} size="lg" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
                      Official Report
                    </h3>
                    <p className="text-gray-700 dark:text-gray-300 mb-3">
                      Published incident reports from police, military, aviation
                      authorities, or government agencies with full details and
                      documentation. These represent confirmed, investigated
                      events.
                    </p>
                    <div className="flex flex-wrap gap-2">
                      <span className="text-xs font-medium px-3 py-1 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-300 rounded-full">
                        Police Reports
                      </span>
                      <span className="text-xs font-medium px-3 py-1 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-300 rounded-full">
                        Military Statements
                      </span>
                      <span className="text-xs font-medium px-3 py-1 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-300 rounded-full">
                        NOTAM Alerts
                      </span>
                      <span className="text-xs font-medium px-3 py-1 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-300 rounded-full">
                        Government Press Conferences
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Score 3 - Verified */}
              <div className="group p-6 rounded-xl bg-gradient-to-r from-amber-50 to-transparent dark:from-amber-950/20 dark:to-transparent border border-amber-200 dark:border-amber-800/30 hover:shadow-md transition-all">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <EvidenceBadge score={3} showTooltip={false} size="lg" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
                      Verified Media Report
                    </h3>
                    <p className="text-gray-700 dark:text-gray-300 mb-3">
                      Confirmed by multiple independent news sources or
                      established media with direct official quotes.
                      Cross-referenced reporting from credible outlets.
                    </p>
                    <div className="flex flex-wrap gap-2">
                      <span className="text-xs font-medium px-3 py-1 bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-300 rounded-full">
                        Multiple News Outlets
                      </span>
                      <span className="text-xs font-medium px-3 py-1 bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-300 rounded-full">
                        Official Quotes
                      </span>
                      <span className="text-xs font-medium px-3 py-1 bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-300 rounded-full">
                        Cross-Referenced
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Score 2 - Reported */}
              <div className="group p-6 rounded-xl bg-gradient-to-r from-orange-50 to-transparent dark:from-orange-950/20 dark:to-transparent border border-orange-200 dark:border-orange-800/30 hover:shadow-md transition-all">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <EvidenceBadge score={2} showTooltip={false} size="lg" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
                      Single Credible Source
                    </h3>
                    <p className="text-gray-700 dark:text-gray-300 mb-3">
                      Verified by a single credible news source or OSINT
                      researcher. Awaiting independent confirmation before
                      upgrading to Verified status.
                    </p>
                    <div className="flex flex-wrap gap-2">
                      <span className="text-xs font-medium px-3 py-1 bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300 rounded-full">
                        Regional News
                      </span>
                      <span className="text-xs font-medium px-3 py-1 bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300 rounded-full">
                        OSINT Analysis
                      </span>
                      <span className="text-xs font-medium px-3 py-1 bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300 rounded-full">
                        Aviation Trackers
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Score 1 - Unconfirmed */}
              <div className="group p-6 rounded-xl bg-gradient-to-r from-red-50 to-transparent dark:from-red-950/20 dark:to-transparent border border-red-200 dark:border-red-800/30 hover:shadow-md transition-all">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <EvidenceBadge score={1} showTooltip={false} size="lg" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
                      Unconfirmed Report
                    </h3>
                    <p className="text-gray-700 dark:text-gray-300 mb-3">
                      Initial reports from social media, local witnesses, or
                      single unconfirmed sources. Treated as unverified until
                      independently confirmed. These may be false alarms.
                    </p>
                    <div className="flex flex-wrap gap-2">
                      <span className="text-xs font-medium px-3 py-1 bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 rounded-full">
                        Social Media
                      </span>
                      <span className="text-xs font-medium px-3 py-1 bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 rounded-full">
                        Unverified Witnesses
                      </span>
                      <span className="text-xs font-medium px-3 py-1 bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 rounded-full">
                        Requires Confirmation
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800/30 rounded-lg">
              <p className="text-sm text-blue-900 dark:text-blue-200">
                <strong>Note:</strong> Scores are automatically calculated based
                on source types and quantity. We prioritize accuracy over
                speed—incidents may start at lower scores and upgrade as
                verification occurs.
              </p>
            </div>
          </div>
        </motion.section>

        {/* Data Collection & Sources */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mb-12"
        >
          <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-200/70 dark:border-gray-800/70 p-8 shadow-soft">
            <div className="flex items-center gap-3 mb-6">
              <div className="flex-shrink-0 w-12 h-12 bg-purple-600 rounded-xl flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"
                  />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Data Collection & Sources
              </h2>
            </div>

            <div className="grid sm:grid-cols-2 gap-6">
              <div className="p-6 bg-gradient-to-br from-blue-50 to-transparent dark:from-blue-950/20 dark:to-transparent rounded-xl border border-blue-200 dark:border-blue-800/30">
                <div className="flex items-center gap-3 mb-3">
                  <svg
                    className="w-5 h-5 text-blue-600 dark:text-blue-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                    />
                  </svg>
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                    Police & Authorities
                  </h3>
                </div>
                <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">
                  Official RSS feeds and press releases from Nordic and European
                  police forces, aviation authorities, and military
                  installations.
                </p>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  Denmark • Norway • Sweden • Finland • Netherlands • Poland
                </div>
              </div>

              <div className="p-6 bg-gradient-to-br from-amber-50 to-transparent dark:from-amber-950/20 dark:to-transparent rounded-xl border border-amber-200 dark:border-amber-800/30">
                <div className="flex items-center gap-3 mb-3">
                  <svg
                    className="w-5 h-5 text-amber-600 dark:text-amber-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"
                    />
                  </svg>
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                    News Media
                  </h3>
                </div>
                <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">
                  Verified reporting from established news outlets, aviation
                  press, and regional newspapers with editorial standards.
                </p>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  Google News alerts • Regional newspapers • Aviation press
                </div>
              </div>

              <div className="p-6 bg-gradient-to-br from-purple-50 to-transparent dark:from-purple-950/20 dark:to-transparent rounded-xl border border-purple-200 dark:border-purple-800/30">
                <div className="flex items-center gap-3 mb-3">
                  <svg
                    className="w-5 h-5 text-purple-600 dark:text-purple-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"
                    />
                  </svg>
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                    Aviation Systems
                  </h3>
                </div>
                <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">
                  NOTAM notices, airport incident reports, air traffic control
                  communications, and aviation safety databases.
                </p>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  NOTAM alerts • Airport reports • ATC communications
                </div>
              </div>

              <div className="p-6 bg-gradient-to-br from-emerald-50 to-transparent dark:from-emerald-950/20 dark:to-transparent rounded-xl border border-emerald-200 dark:border-emerald-800/30">
                <div className="flex items-center gap-3 mb-3">
                  <svg
                    className="w-5 h-5 text-emerald-600 dark:text-emerald-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                    />
                  </svg>
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                    OSINT Community
                  </h3>
                </div>
                <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">
                  Verified reports from open-source intelligence researchers,
                  aviation tracking communities, and security analysts.
                </p>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  OSINT researchers • Aviation trackers • Security analysts
                </div>
              </div>
            </div>
          </div>
        </motion.section>

        {/* Privacy & Transparency */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mb-12"
        >
          <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-200/70 dark:border-gray-800/70 p-8 shadow-soft">
            <div className="flex items-center gap-3 mb-6">
              <div className="flex-shrink-0 w-12 h-12 bg-indigo-600 rounded-xl flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                  />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Privacy & Transparency
              </h2>
            </div>

            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                  <svg
                    className="w-5 h-5 text-blue-600 dark:text-blue-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  Public Data Only
                </h3>
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                  All incident data is sourced exclusively from publicly
                  available reports. We do not collect personal information,
                  track users, or conduct private surveillance. No cookies, no
                  analytics, no tracking.
                </p>
              </div>

              <div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                  <svg
                    className="w-5 h-5 text-emerald-600 dark:text-emerald-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
                    />
                  </svg>
                  Open Source
                </h3>
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed mb-3">
                  DroneWatch is fully open source. Our code, data collection
                  methods, and scoring algorithms are publicly auditable on
                  GitHub. Community contributions are welcome.
                </p>
                <a
                  href="https://github.com/Arnarsson/2"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 transition-colors"
                >
                  View on GitHub
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                    />
                  </svg>
                </a>
              </div>

              <div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                  <svg
                    className="w-5 h-5 text-purple-600 dark:text-purple-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                    />
                  </svg>
                  Research & Journalism Use
                </h3>
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                  The dataset is freely available for academic research,
                  investigative journalism, and policy analysis. We encourage
                  responsible use of this data to improve drone safety and
                  public awareness.
                </p>
              </div>

              <div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                  <svg
                    className="w-5 h-5 text-amber-600 dark:text-amber-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  Data Retention
                </h3>
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                  Incidents remain in the database indefinitely for historical
                  analysis. We do not delete verified incidents, but we may
                  update their status or evidence score as new information
                  becomes available.
                </p>
              </div>
            </div>
          </div>
        </motion.section>

        {/* Contact & Contributing */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="mb-12"
        >
          <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-200/70 dark:border-gray-800/70 p-8 shadow-soft">
            <div className="flex items-center gap-3 mb-6">
              <div className="flex-shrink-0 w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Contact & Feedback
              </h2>
            </div>

            <div className="grid sm:grid-cols-2 gap-6">
              <div className="p-6 bg-gradient-to-br from-blue-50 to-transparent dark:from-blue-950/20 dark:to-transparent rounded-xl border border-blue-200 dark:border-blue-800/30">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
                  Report an Incident
                </h3>
                <p className="text-sm text-gray-700 dark:text-gray-300 mb-4">
                  Have information about a drone incident? Send us the date,
                  location, and source links.
                </p>
                <a
                  href="mailto:report@dronemap.cc"
                  className="inline-flex items-center gap-2 text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 transition-colors"
                >
                  report@dronemap.cc
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M14 5l7 7m0 0l-7 7m7-7H3"
                    />
                  </svg>
                </a>
              </div>

              <div className="p-6 bg-gradient-to-br from-emerald-50 to-transparent dark:from-emerald-950/20 dark:to-transparent rounded-xl border border-emerald-200 dark:border-emerald-800/30">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
                  Contribute on GitHub
                </h3>
                <p className="text-sm text-gray-700 dark:text-gray-300 mb-4">
                  Help improve DroneWatch by contributing code, documentation,
                  or new data sources.
                </p>
                <a
                  href="https://github.com/Arnarsson/2"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-sm font-medium text-emerald-600 dark:text-emerald-400 hover:text-emerald-800 dark:hover:text-emerald-300 transition-colors"
                >
                  github.com/Arnarsson/2
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                    />
                  </svg>
                </a>
              </div>
            </div>
          </div>
        </motion.section>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-gray-900/50 backdrop-blur-xl">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              DroneWatch - Safety Through Transparency
            </p>
            <div className="flex items-center gap-6 text-sm text-gray-600 dark:text-gray-400">
              <a
                href="https://github.com/Arnarsson/2"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-gray-900 dark:hover:text-white transition-colors"
              >
                GitHub
              </a>
              <a
                href="mailto:report@dronemap.cc"
                className="hover:text-gray-900 dark:hover:text-white transition-colors"
              >
                Contact
              </a>
              <span className="text-gray-400 dark:text-gray-600">v1.0</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
