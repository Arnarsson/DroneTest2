const { withSentryConfig } = require('@sentry/nextjs');

/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['unpkg.com'],
  },
  // Enable SWC minification for better performance
  swcMinify: true,
  // Optimize for production
  poweredByHeader: false,
  compress: true,
  // Enable experimental instrumentation for Sentry
  experimental: {
    instrumentationHook: true,
  },
}

module.exports = withSentryConfig(nextConfig, {
  // Suppresses source map uploading logs during build
  silent: true,
  org: "sentry",
  project: "dronewatch",
  // Auth token is not required for local development
  // authToken: process.env.SENTRY_AUTH_TOKEN,
})