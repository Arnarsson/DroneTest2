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
        className="group flex items-center bg-black/95 backdrop-blur-xl rounded-2xl md:rounded-3xl shadow-2xl border border-gray-700/30 px-3 py-2 md:px-4 md:py-2.5 hover:border-gray-600/50 transition-all duration-300"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        {/* Text Only */}
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