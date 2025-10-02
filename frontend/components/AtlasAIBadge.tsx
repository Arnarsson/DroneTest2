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
        href="https://atlasconsulting.dk/"
        target="_blank"
        rel="noopener noreferrer"
        className="group flex items-center bg-black/95 backdrop-blur-xl rounded-xl md:rounded-2xl shadow-lg border border-gray-700/30 px-2 py-1.5 md:px-3 md:py-2 hover:border-gray-600/50 transition-all duration-300"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <div className="flex flex-col">
          <span className="text-[7px] md:text-[8px] uppercase tracking-widest text-gray-400 font-bold leading-none mb-0.5">
            Powered by
          </span>
          <span className="text-[11px] md:text-sm font-bold text-white leading-tight tracking-tight">
            Atlas
          </span>
        </div>
      </motion.a>
    </motion.div>
  )
}