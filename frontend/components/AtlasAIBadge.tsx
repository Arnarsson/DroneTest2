'use client'

import { motion } from 'framer-motion'
import Image from 'next/image'

export function AtlasAIBadge() {
  return (
    <motion.div
      className="fixed bottom-4 right-4 md:bottom-6 md:right-6 z-[100] pointer-events-auto"
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 1, duration: 0.5, type: 'spring', bounce: 0.3 }}
    >
      <motion.a
        href="https://atlas-ai.com"
        target="_blank"
        rel="noopener noreferrer"
        className="block bg-white/90 dark:bg-gray-900/90 backdrop-blur-md rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 p-3 border border-gray-200/50 dark:border-gray-700/50"
        whileHover={{ scale: 1.05, y: -2 }}
        whileTap={{ scale: 0.98 }}
      >
        <Image
          src="/atlas-ai-badge.png"
          alt="Powered by Atlas AI"
          width={150}
          height={50}
          className="w-32 md:w-36 h-auto"
          priority
        />
      </motion.a>
    </motion.div>
  )
}