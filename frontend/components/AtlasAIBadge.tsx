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

          {/* Drone SVG - accurately matches reference design */}
          <svg
            className="w-7 h-7 md:w-9 md:h-9 relative text-white"
            viewBox="0 0 64 64"
            fill="currentColor"
          >
            {/* Left propeller arm */}
            <rect x="2" y="14" width="18" height="4" rx="2" />
            {/* Left rotor end circle */}
            <circle cx="6" cy="16" r="4" />
            {/* Left connector to body */}
            <rect x="18" y="12" width="3" height="8" rx="1.5" />

            {/* Right propeller arm */}
            <rect x="44" y="14" width="18" height="4" rx="2" />
            {/* Right rotor end circle */}
            <circle cx="58" cy="16" r="4" />
            {/* Right connector to body */}
            <rect x="43" y="12" width="3" height="8" rx="1.5" />

            {/* Main vertical body - WIDE pill shape */}
            <rect x="23" y="8" width="18" height="42" rx="9" />

            {/* Large bottom camera ball */}
            <circle cx="32" cy="54" r="9" />

            {/* Medium circle on left side of body */}
            <circle cx="26" cy="32" r="5" />
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