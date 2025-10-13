import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: "https://75bf792b5a278c54e98f72d59d2a7ff5@o4508847842131969.ingest.de.sentry.io/4510181567037520",

  // Adjust this value in production
  tracesSampleRate: 1.0,

  // Enable debug mode in development
  debug: process.env.NODE_ENV === 'development',
});
