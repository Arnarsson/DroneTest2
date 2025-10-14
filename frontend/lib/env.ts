/**
 * Frontend environment variables
 * IMPORTANT: Only NEXT_PUBLIC_* variables are available in browser
 * Server-only secrets (DATABASE_URL, API keys) belong in backend environment
 */
export const ENV = {
  // API endpoint - REQUIRED in production
  API_URL: process.env.NEXT_PUBLIC_API_URL ||
    (process.env.NODE_ENV === 'development'
      ? 'http://localhost:3000/api'  // assumes vercel dev
      : 'https://www.dronemap.cc/api'),  // production fallback

  NODE_ENV: process.env.NODE_ENV || 'development',
} as const;

// Build-time validation (server-side only)
// Note: These warnings are kept as console.warn because they need to appear
// in build logs even in production, and we don't have logger available at build time
if (typeof window === 'undefined') {
  if (!process.env.NEXT_PUBLIC_API_URL && process.env.NODE_ENV === 'production') {
    console.warn('⚠️  NEXT_PUBLIC_API_URL not set - using fallback');
    console.warn('⚠️  Set in Vercel: Settings → Environment Variables');
  }
}

export default ENV;
