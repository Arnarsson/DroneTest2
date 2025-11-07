/**
 * Frontend environment variables
 * IMPORTANT: Only NEXT_PUBLIC_* variables are available in browser
 * Server-only secrets (DATABASE_URL, API keys) belong in backend environment
 */

const isProduction = process.env.NODE_ENV === 'production';
const isServer = typeof window === 'undefined';

export const ENV = {
  // API endpoint - REQUIRED in production
  API_URL: process.env.NEXT_PUBLIC_API_URL ||
    (isProduction
      ? 'https://www.dronemap.cc/api'  // production fallback
      : 'http://localhost:3000/api'),  // development fallback

  NODE_ENV: process.env.NODE_ENV || 'development',
} as const;

// Build-time validation (server-side only)
// Note: These warnings are kept as console.warn because they need to appear
// in build logs even in production, and we don't have logger available at build time
if (isServer) {
  // Validate API URL in production
  if (isProduction && !process.env.NEXT_PUBLIC_API_URL) {
    console.warn('⚠️  NEXT_PUBLIC_API_URL not set - using fallback');
    console.warn('⚠️  Set in Vercel: Settings → Environment Variables');
    console.warn('⚠️  Fallback URL:', ENV.API_URL);
  }
  
  // Validate API URL format
  if (ENV.API_URL && !ENV.API_URL.startsWith('http')) {
    throw new Error(
      `Invalid NEXT_PUBLIC_API_URL format: "${ENV.API_URL}". ` +
      'Expected http:// or https:// URL'
    );
  }
}

export default ENV;
