/**
 * Frontend environment variables
 * IMPORTANT: Only NEXT_PUBLIC_* variables are available in browser
 * Server-only secrets (DATABASE_URL, API keys) belong in backend environment
 */

const isProduction = process.env.NODE_ENV === 'production';
const isServer = typeof window === 'undefined';

// Get API URL - use relative URL in browser, absolute in server
function getApiUrl(): string {
  // If explicitly set, use that
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  
  // In browser, use relative URL (works for both domains)
  if (typeof window !== 'undefined') {
    return '/api';
  }
  
  // Server-side: use production fallback
  if (isProduction) {
    return 'https://www.dronemap.cc/api';
  }
  
  // Development fallback
  return 'http://localhost:3000/api';
}

export const ENV = {
  // API endpoint - uses relative URL in browser for same-origin requests
  API_URL: getApiUrl(),

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
