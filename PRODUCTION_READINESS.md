# Production Readiness Plan

This document tracks the implementation of critical production-ready features for PromptYour.AI authentication and usage management system.

## Implementation Status

- 🔴 Not Started
- 🟡 In Progress
- 🟢 Completed
- ⏸️ Paused/Blocked

---

## Critical Features (Must Have Before Production)

### 1. Password Reset Flow 🟢
**Status**: Completed
**Branch**: `feature/password-reset`
**Priority**: High
**Estimated Time**: 1 day

**Implementation Plan**:
- [x] Create "Forgot Password" page (`/forgot-password`)
- [x] Server action to send reset email
- [x] Create "Reset Password" page (`/reset-password`)
- [x] Token validation and password update logic
- [x] Email template for password reset (using Supabase default)
- [x] Success/error handling and user feedback
- [x] Locale-aware routing

**User Flow**:
```
User clicks "Forgot Password" →
Enters email →
Receives reset email →
Clicks link in email →
Sets new password →
Redirected to login
```

**Files to Create/Modify**:
- `src/app/[locale]/forgot-password/page.tsx`
- `src/app/[locale]/reset-password/page.tsx`
- `src/lib/auth/actions.ts` (add reset functions)
- Update login page with "Forgot Password" link

**Acceptance Criteria**:
- ✅ User can request password reset
- ✅ Reset email sent successfully
- ✅ Token expires after 24 hours (Supabase default)
- ✅ Password updated successfully
- ✅ Works with email verification flow
- ✅ Locale-aware links throughout
- ✅ Error handling for expired/invalid tokens
- ✅ Clear user feedback at each step

**Implementation Notes**:
- Used Supabase's built-in `resetPasswordForEmail()` and `updateUser()` methods
- Reset link redirects to `/auth/reset-password` (non-locale route)
- Forgot password page at `[locale]/forgot-password` for locale support
- Login page includes "Forgot your password?" link
- All success/error states handled with clear messaging
- Password validation: minimum 6 characters, must match confirmation

---

### 4. Rate Limiting 🟢
**Status**: Completed
**Branch**: `feature/rate-limiting`
**Priority**: High
**Estimated Time**: 2 days

**Requirements**:
- Limit users to **5 total chats**
- Each chat limited to **8 messages** (total)
- Message counting:
  - Quick response = 1 message
  - Enhanced response = 2 messages
- Configuration should be in same place as themes/audience/response styles

**Implementation Plan**:
- [x] Add rate limit configuration to YAML config files
- [x] Create rate limiting utility functions
- [x] Track chat count per user in Supabase
- [x] Track message count per chat
- [x] Implement usage checking functions
- [x] Create usage display component for user
- [x] Handle limit exceeded errors gracefully
- [x] Admin override capability (reset function)

**Configuration Structure** (in `config/rate-limits.yaml`):
```yaml
rate_limits:
  max_chats_per_user: 5
  max_messages_per_chat: 8
  message_weights:
    quick_response: 1
    enhanced_response: 2
  reset_period: "monthly" # or "never", "daily", "weekly"
```

**Database Schema** (Supabase):
```sql
-- User usage tracking
CREATE TABLE user_usage (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  chat_count INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id)
);

-- Chat message tracking
CREATE TABLE chat_usage (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  conversation_id TEXT NOT NULL,
  message_count INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, conversation_id)
);
```

**Files to Create/Modify**:
- `config/rate-limits.yaml` (new)
- `src/config/generated-rate-limits.ts` (generated)
- `scripts/generate-config.js` (update to include rate limits)
- `src/lib/usage/tracking.ts` (new - usage tracking functions)
- `src/lib/usage/limits.ts` (new - limit checking functions)
- `src/components/chat/UsageDisplay.tsx` (new - show usage to user)
- `src/components/chat/TwoTierChat.tsx` (integrate usage tracking)
- Database migration SQL files

**User Experience**:
- Display current usage: "Chat 3/5, Messages 6/8"
- Warning at 80% usage: "You're running low on messages"
- Graceful error when limit reached: "You've reached your chat limit. Upgrade to continue."
- Clear call-to-action for upgrade (future)

**Acceptance Criteria**:
- ✅ Rate limits configurable via YAML
- ✅ Chat count tracked per user
- ✅ Message count tracked per chat
- ✅ Enhanced responses count as 2 messages
- ✅ Limits enforced before sending request
- ✅ User can see current usage
- ✅ Clear error messages when limits exceeded
- ✅ Usage resets properly (function available)
- ✅ Visual progress bars with color coding
- ✅ Warning messages at 80% usage
- ✅ Row Level Security for usage data

**Implementation Notes**:
- Created `config/rate-limits.yaml` for easy configuration
- Database tables: `user_usage` (chat count), `chat_usage` (message count per chat)
- Database functions for tracking and querying usage
- TypeScript types in `src/types/usage.ts`
- Query functions in `src/lib/usage/queries.ts`
- Server actions in `src/lib/usage/actions.ts`
- UsageDisplay component shows real-time usage with progress bars
- Color-coded warnings: green → yellow (80%) → red (100%)
- Prevents actions when limits reached with clear error messages
- Admin reset function for manual override
- RLS policies ensure users only see their own usage
- Comprehensive README with integration examples

---

### 5. Error Logging & Monitoring 🟢
**Status**: Completed - **Sentry Free Tier**
**Branch**: `feature/error-logging`
**Priority**: High
**Estimated Time**: 1 week (including discussion and testing)

**Discussion Points**:

#### Option 1: Sentry (Recommended)
**Pros**:
- Industry standard for error tracking
- Real-time error alerts
- Performance monitoring
- User session replay
- Source maps support
- Free tier: 5,000 errors/month

**Cons**:
- Third-party dependency
- Sends data to external service
- Cost increases with scale

**Implementation**:
```typescript
// sentry.client.config.ts
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 1.0,
  environment: process.env.NODE_ENV,
});
```

#### Option 2: Custom Logging (Supabase + Log Service)
**Pros**:
- Full control over data
- No external dependencies
- Can customize everything
- Data stays in your infrastructure

**Cons**:
- More maintenance
- Need to build dashboard
- Time-consuming to implement

**Implementation**:
- Store logs in Supabase
- Create admin dashboard
- Set up alerts manually

#### Option 3: Hybrid Approach
**Pros**:
- Critical errors → Sentry (with alerts)
- General logs → Supabase (for debugging)
- Best of both worlds

**Cons**:
- More complex setup
- Managing two systems

**What to Log**:
- ❌ Authentication failures (with context, NOT passwords)
- ❌ API errors (Supabase, OpenRouter)
- ❌ Rate limit violations
- ❌ Email delivery failures
- ❌ Payment failures (future)
- ❌ Unusual activity patterns
- ❌ Performance issues
- ❌ JavaScript errors (client-side)

**What NOT to Log**:
- ✅ Passwords
- ✅ API keys
- ✅ Personal identification data (be GDPR compliant)
- ✅ Full email content

**Decision Made**: ✅ **Sentry Free Tier** (Option 1)

User Requirements:
1. ✅ Minimal/no cost → **Free tier (5,000 errors/month, $0)**
2. ✅ No real-time monitoring needed → **Disabled alerts**
3. ✅ No session replay needed → **Disabled replay**
4. ✅ Simple setup → **Automatic error tracking**

**Implementation Completed**:

**Files Created**:
- ✅ `sentry.client.config.ts` - Client-side error tracking
- ✅ `sentry.server.config.ts` - Server-side error tracking
- ✅ `sentry.edge.config.ts` - Edge runtime error tracking
- ✅ `next.config.js` - Updated with Sentry integration
- ✅ `SENTRY_SETUP.md` - Complete setup guide
- ✅ `.env.example` - Environment variable template

**Features Implemented**:
- Automatic JavaScript/TypeScript error tracking
- API error tracking (Supabase, OpenRouter, etc.)
- Performance monitoring (page loads, API calls)
- User context tracking
- Stack traces with source maps
- Error filtering (404s, auth errors, rate limits excluded)
- Free tier optimizations (no session replay, no source map upload)

**Error Filtering**:
The following errors are NOT tracked (to save quota):
- 404 errors (expected user behavior)
- "Email not confirmed" (expected auth flow)
- Rate limit errors (expected when limits hit)

**Setup Required**:
1. Create free Sentry account at sentry.io
2. Create Next.js project in Sentry
3. Copy DSN to `.env.local`:
   ```
   NEXT_PUBLIC_SENTRY_DSN=https://xxxxx@o000000.ingest.sentry.io/0000000
   ```
4. Restart dev server

See `SENTRY_SETUP.md` for complete instructions.

**Cost**: $0/month (Free tier: 5,000 errors/month)

---

## Important Features (Should Have Soon)

### 8. Custom User Data Storage 🟢
**Status**: Completed
**Branch**: `feature/user-profiles`
**Priority**: Medium-High
**Estimated Time**: 2 days

**Implementation Plan**:
- [x] Design user profiles schema
- [x] Create Supabase tables with RLS policies
- [x] Implement automatic profile creation on signup
- [x] Create profile management pages
- [x] Add profile edit functionality
- [x] Display user preferences in UI

**Database Schema**:
```sql
-- User profiles table
CREATE TABLE public.user_profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  email TEXT,
  full_name TEXT,
  display_name TEXT,
  avatar_url TEXT,
  bio TEXT,

  -- Preferences
  default_theme TEXT,
  default_audience TEXT,
  default_response_style TEXT,

  -- Usage tracking (reference)
  total_chats INT DEFAULT 0,
  total_messages INT DEFAULT 0,

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  CONSTRAINT fk_user FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE
);

-- Enable RLS
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Users can view own profile"
  ON public.user_profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON public.user_profiles FOR UPDATE
  USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
  ON public.user_profiles FOR INSERT
  WITH CHECK (auth.uid() = id);

-- Trigger for auto-profile creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_profiles (id, email, full_name, avatar_url)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email),
    NEW.raw_user_meta_data->>'avatar_url'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();
```

**Files to Create**:
- `src/lib/supabase/queries/profiles.ts` (CRUD operations)
- `src/app/[locale]/profile/page.tsx` (profile view)
- `src/app/[locale]/profile/edit/page.tsx` (profile edit)
- `src/components/profile/ProfileView.tsx`
- `src/components/profile/ProfileEdit.tsx`
- Database migration SQL file

**Acceptance Criteria**:
- ✅ Profile created automatically on signup (via database trigger)
- ✅ OAuth data populates profile (name, avatar)
- ✅ User can view their profile at `/[locale]/profile`
- ✅ User can edit profile fields at `/[locale]/profile/edit`
- ✅ RLS policies prevent unauthorized access
- ✅ Preferences saved (theme, audience, response style)
- ✅ Usage statistics tracked (total chats, total messages)
- ✅ Profile accessible from user menu dropdown

**Implementation Notes**:
- Created `user_profiles` table with full RLS policies
- Automatic profile creation via `handle_new_user()` trigger
- Auto-updates `updated_at` timestamp on profile changes
- TypeScript types in `src/types/profile.ts`
- Query functions in `src/lib/supabase/queries/profiles.ts`
- Server actions in `src/lib/profile/actions.ts`
- Profile view page with all user information displayed
- Profile edit page with form validation
- Usage tracking functions: `increment_chat_count()` and `increment_message_count()`
- User menu updated with "Your Profile" link
- Migration files with rollback instructions in `migrations/README.md`

---

### 9. Session Management 🔴
**Status**: Not Started
**Branch**: `feature/session-management`
**Priority**: Medium
**Estimated Time**: 2 days

**Implementation Plan**:
- [ ] Create sessions list page
- [ ] Display active sessions (device, location, time)
- [ ] Implement revoke session functionality
- [ ] Add "logout all devices" feature
- [ ] Session activity tracking
- [ ] Security alerts for new devices

**Features**:
1. **View Active Sessions**:
   - Current session highlighted
   - Device type (browser, OS)
   - Last active timestamp
   - IP address (optional, privacy consideration)

2. **Revoke Sessions**:
   - Revoke individual session
   - Revoke all other sessions
   - Can't revoke current session (logout instead)

3. **Session Notifications** (optional):
   - Email alert on login from new device
   - Alert on login from new location

**Files to Create**:
- `src/app/[locale]/profile/sessions/page.tsx`
- `src/lib/supabase/queries/sessions.ts`
- `src/components/profile/SessionsList.tsx`
- `src/components/profile/SessionItem.tsx`
- `src/lib/auth/sessions.ts` (session management logic)

**Supabase Integration**:
```typescript
// Get all user sessions
const { data: sessions } = await supabase.auth.admin.getUserSessions(userId);

// Revoke session
await supabase.auth.admin.deleteSession(sessionId);
```

**Acceptance Criteria**:
- ✅ User can see all active sessions
- ✅ Current session is highlighted
- ✅ User can revoke individual sessions
- ✅ User can revoke all other sessions
- ✅ Session list updates in real-time
- ✅ Clear confirmation before revoking

---

## Progress Tracking

### Sprint 1: Critical Security Features
**Timeline**: Week 1-2
**Status**: 🟢 Completed

- [x] Password Reset Flow ✅ (Completed)
- [x] Rate Limiting ✅ (Completed)
- [x] Error Logging & Monitoring ✅ (Completed - Sentry Free Tier)

### Sprint 2: User Management
**Timeline**: Week 3-4
**Status**: 🟡 In Progress

- [x] Custom User Data Storage ✅ (Completed)
- [ ] Session Management

---

## Implementation Order

1. **First**: Create PRODUCTION_READINESS.md ✅
2. **Next**: Password Reset Flow (independent feature)
3. **Then**: Custom User Data Storage (needed for rate limiting)
4. **Then**: Rate Limiting (depends on user profiles)
5. **Parallel**: Error Logging & Monitoring (can be done alongside)
6. **Finally**: Session Management (depends on profiles)

---

## Branch Strategy

Each feature has its own branch:
- `feature/password-reset`
- `feature/rate-limiting`
- `feature/error-logging`
- `feature/user-profiles`
- `feature/session-management`

**Workflow**:
1. Create feature branch from `main`
2. Implement feature
3. Test thoroughly
4. Commit with detailed message
5. Push to origin
6. Create PR (if needed) or merge to main
7. Update this document with progress

---

## Testing Checklist

For each feature:
- [ ] Unit tests written
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Edge cases tested
- [ ] Error handling validated
- [ ] Security review done
- [ ] Documentation updated

---

## Rollout Plan

### Phase 1: Development (Current)
- Implement features in branches
- Test locally
- Validate with test users

### Phase 2: Staging
- Deploy to staging environment
- Run full test suite
- Load testing
- Security audit

### Phase 3: Production
- Feature flags for gradual rollout
- Monitor errors closely
- Have rollback plan ready

---

## Success Metrics

- [ ] Zero authentication-related errors
- [ ] Email delivery rate >95%
- [ ] Password reset success rate >90%
- [ ] Rate limiting working correctly
- [ ] All errors logged and monitored
- [ ] User profiles working correctly
- [ ] Session management functional

---

## Notes & Decisions

### 2025-01-XX: Error Logging Discussion
- **Decision**: TBD after discussion
- **Considerations**: Budget, privacy, complexity

### 2025-01-XX: Rate Limiting Design
- **Decision**: YAML config + Supabase tracking
- **Rationale**: Consistent with existing config pattern, easy to modify

---

## Last Updated
**Date**: 2025-01-13
**By**: Claude Code
**Version**: 1.0
