import * as Sentry from "@sentry/nextjs";

// Generate release name from package.json version + git commit or timestamp
const RELEASE = process.env.SENTRY_RELEASE ||
  process.env.NEXT_PUBLIC_VERCEL_GIT_COMMIT_SHA ||
  `dronewatch@${process.env.npm_package_version || '0.1.0'}`;

Sentry.init({
  dsn: "https://75bf792b5a278c54e98f72d59d2a7ff5@o4508847842131969.ingest.de.sentry.io/4510181567037520",

  // Release tracking for health monitoring
  release: RELEASE,
  environment: process.env.NODE_ENV || 'development',

  // Adjust this value in production
  tracesSampleRate: 1.0,

  // Enable debug mode in development
  debug: process.env.NODE_ENV === 'development',
});
