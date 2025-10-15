# Sentry Error Logging Setup Guide

This guide will help you set up Sentry for error tracking with the **free tier** (5,000 errors/month, $0 cost).

## Why Sentry?

- ✅ **Free tier**: 5,000 errors/month at no cost
- ✅ **Automatic error tracking**: Catches JavaScript, TypeScript, and API errors
- ✅ **Source maps**: See exactly where errors occur in your code
- ✅ **Performance monitoring**: Track slow API calls and page loads
- ✅ **User context**: See which users are affected by errors
- ✅ **Stack traces**: Full error details for debugging

## Step 1: Create Sentry Account

1. Go to [sentry.io](https://sentry.io/signup/)
2. Sign up for a free account (no credit card required)
3. Choose **"Create a new project"**
4. Select **Next.js** as the platform
5. Name your project (e.g., "promptyour-ai")
6. Click **"Create Project"**

## Step 2: Get Your DSN

After creating the project, Sentry will show you a **DSN** (Data Source Name). It looks like:

```
https://xxxxxxxxxxxxx@o000000.ingest.sentry.io/0000000
```

Copy this DSN - you'll need it in the next step.

## Step 3: Configure Environment Variables

Add the following to your `.env.local` file:

```env
# Sentry Configuration
NEXT_PUBLIC_SENTRY_DSN=https://xxxxxxxxxxxxx@o000000.ingest.sentry.io/0000000

# Optional: Only needed if you want to upload source maps (not required for free tier)
SENTRY_ORG=your-org-name
SENTRY_PROJECT=your-project-name
SENTRY_AUTH_TOKEN=your-auth-token
```

**Important**:
- Replace the DSN with your actual DSN from Sentry
- The `SENTRY_ORG`, `SENTRY_PROJECT`, and `SENTRY_AUTH_TOKEN` are optional for the free tier
- **Never commit `.env.local` to git** - it's already in `.gitignore`

## Step 4: Restart Development Server

```bash
npm run dev
```

That's it! Sentry is now tracking errors.

## Step 5: Test the Setup

Create a test error to verify Sentry is working:

1. Add a test button to any page:

```tsx
<button onClick={() => {
  throw new Error('Test Sentry error!');
}}>
  Test Sentry
</button>
```

2. Click the button
3. Check your Sentry dashboard - you should see the error within a few seconds

## What Gets Tracked?

### Automatically Tracked
- ✅ **JavaScript errors**: Uncaught exceptions, promise rejections
- ✅ **TypeScript errors**: Type errors, null references
- ✅ **API errors**: Failed fetch requests, Supabase errors
- ✅ **Performance issues**: Slow page loads, slow API calls

### Filtered Out (Not Tracked)
- ❌ **404 errors**: Expected user behavior
- ❌ **Authentication errors**: "Email not confirmed" (expected)
- ❌ **Rate limit errors**: Expected when users hit limits

## Configuration Details

### Free Tier Optimizations

We've configured Sentry to work optimally with the free tier:

- **No session replay**: Disabled to save quota (can enable if needed)
- **No source map upload**: Disabled to save build time and quota
- **Error filtering**: Only tracks unexpected errors
- **Sample rate**: 100% (all errors tracked, but filtered intelligently)

### Error Filtering

The following errors are **not** sent to Sentry:

```typescript
// sentry.client.config.ts and sentry.server.config.ts
beforeSend(event, hint) {
  // Don't send 404 errors
  if (event.exception?.values?.[0]?.value?.includes('404')) {
    return null;
  }

  // Don't send authentication errors (expected user behavior)
  if (event.exception?.values?.[0]?.value?.includes('Email not confirmed')) {
    return null;
  }

  // Don't send rate limit errors
  if (event.exception?.values?.[0]?.value?.includes('limit reached')) {
    return null;
  }

  return event;
}
```

You can add more filters as needed.

## Manual Error Tracking

### Capture Specific Errors

```typescript
import * as Sentry from '@sentry/nextjs';

try {
  // Your code
} catch (error) {
  // Log to Sentry with context
  Sentry.captureException(error, {
    contexts: {
      user: {
        id: userId,
        email: userEmail,
      },
    },
    tags: {
      section: 'payment',
      action: 'checkout',
    },
  });
}
```

### Capture Custom Messages

```typescript
import * as Sentry from '@sentry/nextjs';

// Log a warning
Sentry.captureMessage('Something unusual happened', 'warning');

// Log an error with context
Sentry.captureMessage('Payment failed', {
  level: 'error',
  contexts: {
    payment: {
      amount: 100,
      currency: 'USD',
    },
  },
});
```

### Add User Context

```typescript
import * as Sentry from '@sentry/nextjs';

// Set user context for all future errors
Sentry.setUser({
  id: user.id,
  email: user.email,
  username: user.display_name,
});

// Clear user context (on logout)
Sentry.setUser(null);
```

## Monitoring the Dashboard

### View Errors

1. Go to [sentry.io](https://sentry.io/)
2. Select your project
3. Click **Issues** to see all errors
4. Click on any error to see:
   - Stack trace
   - User information
   - Breadcrumbs (what led to the error)
   - Device/browser info

### Understanding Error Metrics

- **Total Events**: Number of times this error occurred
- **Users Affected**: How many users experienced this error
- **Last Seen**: When this error last occurred
- **First Seen**: When this error was first detected

## Best Practices

### ✅ Do

- Log unexpected errors that need investigation
- Add user context to help debug issues
- Use tags to categorize errors
- Review errors regularly

### ❌ Don't

- Log expected user behavior (404s, invalid input)
- Log sensitive data (passwords, API keys)
- Log authentication failures (unless suspicious)
- Leave errors unresolved for weeks

## Privacy & GDPR

### What Data Does Sentry Collect?

- Error messages and stack traces
- User context (if you provide it)
- Device/browser information
- Page URLs where errors occurred
- Custom context you add

### GDPR Compliance

- Data is stored in the EU (select EU region when creating project)
- Users can request data deletion
- No personal data sent without your explicit code
- Configure data scrubbing in Sentry settings

### Disable for Specific Users

```typescript
// Don't track errors for specific users
if (user.isTestUser) {
  Sentry.init({
    enabled: false,
  });
}
```

## Troubleshooting

### Errors Not Appearing in Sentry

1. **Check DSN**: Verify `NEXT_PUBLIC_SENTRY_DSN` is set correctly
2. **Restart server**: Environment variables require restart
3. **Check browser console**: Look for Sentry initialization errors
4. **Verify project**: Make sure you're looking at the correct project in Sentry

### Too Many Errors (Over 5,000/month)

1. **Add more filters**: Filter out noisy errors in `beforeSend`
2. **Reduce sample rate**: Change `tracesSampleRate` to 0.1 (10%)
3. **Check for error loops**: Fix errors that occur repeatedly

### Source Maps Not Working

Source maps are disabled for the free tier to save quota. If you need them:

1. Set `SENTRY_AUTH_TOKEN` in `.env.local`
2. Enable webpack plugins in `next.config.js`:
   ```js
   disableServerWebpackPlugin: false,
   disableClientWebpackPlugin: false,
   ```

## Upgrading from Free Tier

If you exceed 5,000 errors/month or need premium features:

- **Team Plan**: $29/month
  - 50,000 errors/month
  - Multiple projects
  - Team collaboration
  - Session replay

- **Business Plan**: $99/month
  - 500,000 errors/month
  - Priority support
  - Advanced features

## Resources

- [Sentry Next.js Docs](https://docs.sentry.io/platforms/javascript/guides/nextjs/)
- [Error Filtering](https://docs.sentry.io/platforms/javascript/guides/nextjs/configuration/filtering/)
- [Performance Monitoring](https://docs.sentry.io/platforms/javascript/guides/nextjs/performance/)
- [Privacy & Security](https://docs.sentry.io/security-legal-pii/)

## Support

- **Sentry Support**: [support@sentry.io](mailto:support@sentry.io)
- **Community Forum**: [forum.sentry.io](https://forum.sentry.io/)
- **Discord**: [discord.gg/sentry](https://discord.gg/sentry)
