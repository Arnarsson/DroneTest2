'use client';

import { useLocale, useTranslations } from 'next-intl';
import { usePathname, useRouter } from 'next/navigation';
import { useTransition } from 'react';

export function LanguageSwitcher() {
  const t = useTranslations('language');
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  const [isPending, startTransition] = useTransition();

  const handleChange = (newLocale: string) => {
    startTransition(() => {
      // Remove current locale from pathname if it exists
      const pathnameWithoutLocale = pathname.replace(/^\/(en|da|de)/, '') || '/';

      // Add new locale prefix (except for default 'en')
      const newPath = newLocale === 'en' ? pathnameWithoutLocale : `/${newLocale}${pathnameWithoutLocale}`;

      router.replace(newPath);
    });
  };

  return (
    <div className="relative">
      <select
        value={locale}
        onChange={(e) => handleChange(e.target.value)}
        disabled={isPending}
        className="text-sm border border-gray-300 dark:border-gray-700 rounded-md px-3 py-1.5 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600 transition-colors cursor-pointer disabled:opacity-50"
        aria-label={t('select')}
      >
        <option value="en">🇬🇧 {t('en')}</option>
        <option value="da">🇩🇰 {t('da')}</option>
        <option value="de">🇩🇪 {t('de')}</option>
      </select>
    </div>
  );
}