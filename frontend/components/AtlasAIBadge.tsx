'use client'

import { motion } from 'framer-motion'

export function AtlasAIBadge() {
  return (
    <motion.div
      className="fixed bottom-4 left-4 md:bottom-6 md:left-6 z-[100] pointer-events-auto"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 1.5, duration: 0.6, ease: 'easeOut' }}
    >
      <motion.a
        href="https://atlas-ai.com"
        target="_blank"
        rel="noopener noreferrer"
        className="group flex items-center gap-2 md:gap-3 bg-black/95 backdrop-blur-xl rounded-2xl md:rounded-3xl shadow-2xl border border-gray-700/30 px-3 py-2 md:px-5 md:py-3 hover:border-gray-600/50 transition-all duration-300"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        {/* Drone Icon */}
        <div className="relative">
          {/* Animated glow effect */}
          <motion.div
            className="absolute inset-0 bg-white/30 rounded-full blur-lg"
            animate={{
              opacity: [0.3, 0.6, 0.3],
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />

          {/* Static outer glow */}
          <div className="absolute inset-0 bg-white/20 rounded-full blur-md group-hover:bg-white/40 transition-all" />

          {/* Drone SVG */}
          <svg
            className="w-5 h-5 md:w-7 md:h-7 relative text-white"
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            {/* Top propellers */}
            <circle cx="7" cy="5" r="1.5" />
            <circle cx="17" cy="5" r="1.5" />
            {/* Body - rounded capsule shape */}
            <rect x="10" y="8" width="4" height="8" rx="2" />
            {/* Camera/sensor circle */}
            <circle cx="12" cy="16" r="2.5" />
            {/* Propeller connectors */}
            <rect x="6" y="6" width="2" height="3" rx="0.5" />
            <rect x="16" y="6" width="2" height="3" rx="0.5" />
          </svg>
        </div>

        {/* Text */}
        <div className="flex flex-col">
          <span className="text-[9px] md:text-[11px] uppercase tracking-widest text-gray-400 font-bold leading-none mb-0.5">
            Powered by
          </span>
          <span className="text-sm md:text-base font-bold text-white leading-tight tracking-tight">
            Atlas AI
          </span>
        </div>
      </motion.a>
    </motion.div>
  )
}