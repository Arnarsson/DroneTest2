'use client';

import { useTranslations } from 'next-intl';
import { ThemeToggle } from './ThemeToggle';
import { LanguageSwitcher } from './LanguageSwitcher';

export function Header({ incidentCount, isLoading }: {
  incidentCount: number
  isLoading: boolean
}) {
  const t = useTranslations('header');
  const tCommon = useTranslations('common');

  return (
    <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 shadow-sm transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <span className="text-3xl">🚁</span>
              {t('title')}
            </h1>
            <span className="ml-4 text-sm text-gray-500 dark:text-gray-400 hidden sm:inline">
              {t('subtitle')}
            </span>
          </div>

          <div className="flex items-center gap-4">
            {/* Live indicator */}
            <div className="flex items-center gap-2">
              <div className={`h-3 w-3 rounded-full ${isLoading ? 'bg-yellow-400' : 'bg-green-500'} animate-pulse`} />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                {isLoading ? `${tCommon('loading')}` : `${incidentCount} ${tCommon('incidents')}`}
              </span>
            </div>

            {/* Language switcher */}
            <LanguageSwitcher />

            {/* Theme toggle */}
            <ThemeToggle />

            {/* Info button */}
            <button
              onClick={() => window.open('/about', '_blank')}
              className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 p-2 transition-colors"
              title={tCommon('about')}
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