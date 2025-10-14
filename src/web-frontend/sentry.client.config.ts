// This file configures the initialization of Sentry on the client.
// The config you add here will be used whenever a users loads a page in their browser.
// https://docs.sentry.io/platforms/javascript/guides/nextjs/

import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,

  // Adjust this value in production, or use tracesSampler for greater control
  tracesSampleRate: 1,

  // Setting this option to true will print useful information to the console while you're setting up Sentry.
  debug: false,

  // Replay configuration for session replay (disabled for free tier to save on quota)
  replaysOnErrorSampleRate: 0, // Changed from 1.0 to 0 to disable
  replaysSessionSampleRate: 0, // Changed from 0.1 to 0 to disable

  // Environment configuration
  environment: process.env.NODE_ENV,

  // You can remove this option if you're not planning to use the Sentry Session Replay feature:
  integrations: [
    // Sentry.replayIntegration({
    //   // Disabled for free tier
    // }),
  ],

  // Filter out expected errors
  beforeSend(event, hint) {
    // Don't send 404 errors
    if (event.exception?.values?.[0]?.value?.includes('404')) {
      return null;
    }

    // Don't send authentication errors (expected user behavior)
    if (event.exception?.values?.[0]?.value?.includes('Email not confirmed')) {
      return null;
    }

    return event;
  },
});
