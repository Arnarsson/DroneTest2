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

          {/* Drone SVG - matches reference EXACTLY */}
          <svg
            className="w-8 h-8 md:w-10 md:h-10 relative text-white"
            viewBox="0 0 100 100"
            fill="currentColor"
          >
            {/* MAIN VERTICAL BODY - Large pill on RIGHT side (most prominent) */}
            <rect x="50" y="15" width="28" height="70" rx="14" />

            {/* LARGE BOTTOM-LEFT CIRCLE - Camera gimbal */}
            <circle cx="25" cy="75" r="18" />

            {/* MEDIUM MIDDLE-LEFT CIRCLE - Secondary component */}
            <circle cx="30" cy="45" r="11" />

            {/* LEFT PROPELLER ARM - at top */}
            <rect x="8" y="18" width="24" height="5" rx="2.5" />
            {/* Left rotor circle at end */}
            <circle cx="13" cy="20.5" r="5" />
            {/* Left vertical connector to body */}
            <rect x="30" y="15" width="3" height="10" rx="1.5" />

            {/* RIGHT PROPELLER ARM - at top */}
            <rect x="68" y="18" width="24" height="5" rx="2.5" />
            {/* Right rotor circle at end */}
            <circle cx="87" cy="20.5" r="5" />
            {/* Right vertical connector to body */}
            <rect x="67" y="15" width="3" height="10" rx="1.5" />
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