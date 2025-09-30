import createMiddleware from 'next-intl/middleware';

export default createMiddleware({
  // A list of all locales that are supported
  locales: ['en', 'da', 'de'],

  // Used when no locale matches
  defaultLocale: 'en',

  // Don't use locale prefix for default locale
  localePrefix: 'as-needed'
});

export const config = {
  // Match only internationalized pathnames
  matcher: ['/', '/(da|de|en)/:path*', '/((?!api|_next|_vercel|.*\\..*).*)']
};