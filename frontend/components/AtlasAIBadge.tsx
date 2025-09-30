'use client'

import { motion } from 'framer-motion'

export function AtlasAIBadge() {
  return (
    <motion.div
      className="fixed bottom-4 right-4 md:bottom-6 md:right-6 z-[100] pointer-events-auto"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 1.5, duration: 0.6, ease: 'easeOut' }}
    >
      <motion.a
        href="https://atlas-ai.com"
        target="_blank"
        rel="noopener noreferrer"
        className="group flex items-center gap-2 bg-gradient-to-r from-slate-900/95 to-slate-800/95 dark:from-slate-950/95 dark:to-slate-900/95 backdrop-blur-xl rounded-full shadow-xl border border-slate-700/50 dark:border-slate-600/50 px-4 py-2.5 hover:shadow-2xl hover:shadow-blue-500/20 transition-all duration-300"
        whileHover={{ scale: 1.02, x: -2 }}
        whileTap={{ scale: 0.98 }}
      >
        <div className="flex items-center gap-2">
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full blur-sm opacity-75 group-hover:opacity-100 transition-opacity" />
            <svg
              className="w-5 h-5 relative text-blue-400 group-hover:text-blue-300 transition-colors"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 10V3L4 14h7v7l9-11h-7z"
              />
            </svg>
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold leading-none">
              POWERED BY
            </span>
            <span className="text-sm font-bold text-white leading-tight tracking-tight">
              Atlas AI
            </span>
          </div>
        </div>
        <div className="ml-1 opacity-50 group-hover:opacity-100 group-hover:translate-x-0.5 transition-all">
          <svg
            className="w-3.5 h-3.5 text-slate-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5l7 7-7 7"
            />
          </svg>
        </div>
      </motion.a>
    </motion.div>
  )
}