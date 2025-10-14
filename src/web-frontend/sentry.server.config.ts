// This file configures the initialization of Sentry for edge features (middleware, edge routes, and so on).
// The config you add here will be used whenever one of the edge features is loaded.
// Note that this config is unrelated to the Vercel Edge Runtime and is also required when running locally.
// https://docs.sentry.io/platforms/javascript/guides/nextjs/

import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,

  // Adjust this value in production, or use tracesSampler for greater control
  tracesSampleRate: 1,

  // Setting this option to true will print useful information to the console while you're setting up Sentry.
  debug: false,

  // Environment configuration
  environment: process.env.NODE_ENV,

  // Filter out expected errors
  beforeSend(event, hint) {
    // Don't send expected authentication errors
    if (event.exception?.values?.[0]?.value?.includes('Email not confirmed')) {
      return null;
    }

    // Don't send rate limit errors (these are expected user behavior)
    if (event.exception?.values?.[0]?.value?.includes('limit reached')) {
      return null;
    }

    return event;
  },
});
