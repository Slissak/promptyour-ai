const createNextIntlPlugin = require('next-intl/plugin');
const { withSentryConfig } = require('@sentry/nextjs');

const withNextIntl = createNextIntlPlugin('./src/i18n/request.ts');

/** @type {import('next').NextConfig} */
const nextConfig = {
  typedRoutes: true,
  // Enable static optimization for better performance
  output: 'standalone',
  // PWA support for mobile
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
        ],
      },
    ];
  },
};

// Sentry configuration options
const sentryWebpackPluginOptions = {
  // For all available options, see:
  // https://github.com/getsentry/sentry-webpack-plugin#options

  // Suppresses source map uploading logs during build (free tier doesn't need source maps uploaded)
  silent: true,

  // Disable source map upload for free tier to save on quota
  disableServerWebpackPlugin: true,
  disableClientWebpackPlugin: true,

  org: process.env.SENTRY_ORG,
  project: process.env.SENTRY_PROJECT,
};

// Wrap the config with both next-intl and Sentry
module.exports = withSentryConfig(
  withNextIntl(nextConfig),
  sentryWebpackPluginOptions
);