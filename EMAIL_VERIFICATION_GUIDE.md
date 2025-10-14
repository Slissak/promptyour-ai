# Email Verification Setup Guide

## Quick Fix: Enable Immediate Login (For Testing)

If you want to test the app without email verification delays:

1. Go to [Supabase Dashboard](https://app.supabase.com/)
2. Select your project
3. Navigate to **Authentication** → **Providers** → **Email**
4. Scroll to **Confirm email** section
5. **Toggle OFF** "Confirm email"
6. Click **Save**
7. Delete any stuck accounts in **Authentication** → **Users**
8. Try signing up again!

---

## Industry Best Practice: Email Verification Flow

### What We Implemented

✅ **Signup Flow**:
- User signs up with email/password
- Receives clear message about email verification
- Can't login until email is confirmed

✅ **Login Flow**:
- User trying to login with unverified email gets helpful error
- "Resend verification email" button appears automatically
- One-click resend functionality

✅ **Verification Flow**:
- User clicks link in email
- Automatically redirected to app
- Can now log in

---

## How to Configure Email Sending

### Option 1: Use Supabase Built-in Email (Development)

**Limitations**:
- Rate limited to 4 emails per hour
- Emails often go to spam
- Only for development/testing

**Setup**: No configuration needed, it works by default!

### Option 2: Custom SMTP (Production Recommended)

**Providers**:
- **SendGrid** (free tier: 100 emails/day)
- **Mailgun** (free tier: 5,000 emails/month for 3 months)
- **AWS SES** (very cheap, reliable)
- **Postmark** (great deliverability)

**Setup Steps**:
1. Sign up for email provider (e.g., SendGrid)
2. Get SMTP credentials
3. In Supabase Dashboard:
   - Go to **Project Settings** → **Auth**
   - Scroll to **SMTP Settings**
   - Toggle **Enable Custom SMTP**
   - Fill in:
     - SMTP Host: `smtp.sendgrid.net` (or your provider)
     - Port: `587` (or `465` for SSL)
     - Username: Your SMTP username
     - Password: Your SMTP password
     - Sender email: `noreply@yourdomain.com`
     - Sender name: `PromptYour.AI`
4. Click **Save**

### Option 3: Email Service with API (Advanced)

Integrate directly with:
- **Resend** (developer-friendly, 3,000 free emails/month)
- **Brevo (Sendinblue)** (300 emails/day free)

---

## Customize Email Templates

### Supabase Email Templates

1. Go to **Authentication** → **Email Templates**
2. You'll see templates for:
   - **Confirm signup** - Sent when user signs up
   - **Magic Link** - Passwordless login
   - **Change Email Address** - Email change confirmation
   - **Reset Password** - Password reset

### Customize Confirmation Email

Edit the **Confirm signup** template:

```html
<h2>Confirm your email</h2>
<p>Welcome to PromptYour.AI!</p>
<p>Click the button below to confirm your email address:</p>
<p><a href="{{ .ConfirmationURL }}">Confirm Email</a></p>
<p>If you didn't create an account, you can safely ignore this email.</p>
```

Variables available:
- `{{ .ConfirmationURL }}` - Verification link
- `{{ .Token }}` - Verification token
- `{{ .SiteURL }}` - Your app URL
- `{{ .RedirectTo }}` - Redirect destination after verification

---

## Email Verification States

### User States in Supabase

1. **Unconfirmed**:
   - User signed up but hasn't clicked email link
   - Can't login
   - `email_confirmed_at` = null

2. **Confirmed**:
   - User clicked verification link
   - Can login
   - `email_confirmed_at` = timestamp

### Check User Status

```sql
-- See all unverified users
SELECT
  email,
  created_at,
  email_confirmed_at,
  CASE
    WHEN email_confirmed_at IS NULL THEN 'Unverified'
    ELSE 'Verified'
  END as status
FROM auth.users
WHERE email_confirmed_at IS NULL
ORDER BY created_at DESC;
```

---

## Testing Email Verification

### Development Testing

1. **Use Mailtrap** (free email testing):
   - Sign up at [mailtrap.io](https://mailtrap.io/)
   - Get SMTP credentials
   - Configure in Supabase
   - All emails go to Mailtrap inbox (not real users)

2. **Use Your Own Email**:
   - Sign up with your email
   - Check spam folder
   - Click verification link

### Production Testing

1. Sign up with test account
2. Check email deliverability
3. Verify links work correctly
4. Test resend functionality
5. Monitor for spam issues

---

## Common Issues & Solutions

### Issue 1: Emails Not Received

**Causes**:
- Emails going to spam
- SMTP not configured
- Rate limits hit (Supabase default: 4/hour)

**Solutions**:
- Configure custom SMTP provider
- Add SPF/DKIM records to your domain
- Use dedicated email service
- Check spam folder

### Issue 2: User Can't Login

**Cause**: Email not verified

**Solution**:
1. User clicks "Resend verification email" on login page
2. Check spam folder for email
3. Or delete user and recreate:
   ```sql
   DELETE FROM auth.users WHERE email = 'user@example.com';
   ```

### Issue 3: Verification Link Expired

**Cause**: Links expire after 24 hours (default)

**Solution**:
- User clicks "Resend verification email"
- New link is generated
- Update expiry in Supabase settings

### Issue 4: Emails Going to Spam

**Solutions**:
1. **Add SPF Record** to your DNS:
   ```
   v=spf1 include:_spf.sendgrid.net ~all
   ```

2. **Add DKIM Record** (provided by email service)

3. **Use Authenticated Domain**:
   - Don't use `@gmail.com` as sender
   - Use `noreply@yourdomain.com`

4. **Warm Up Your Email Domain**:
   - Start with low volume
   - Gradually increase over weeks

---

## Security Best Practices

### ✅ What We Implemented

1. **Email Verification Required**: Prevents fake accounts
2. **Resend Rate Limiting**: Prevents spam (built into Supabase)
3. **Token Expiration**: Links expire after 24 hours
4. **Secure Redirects**: Verified redirect URLs only

### Additional Security

1. **Add CAPTCHA on Signup**:
   ```typescript
   // Add Google reCAPTCHA
   import { ReCaptcha } from 'next-recaptcha-v3';
   ```

2. **Monitor Suspicious Activity**:
   ```sql
   -- Find users who signed up but never verified
   SELECT COUNT(*)
   FROM auth.users
   WHERE email_confirmed_at IS NULL
   AND created_at < NOW() - INTERVAL '7 days';
   ```

3. **Delete Unverified Users** (after 7 days):
   ```sql
   DELETE FROM auth.users
   WHERE email_confirmed_at IS NULL
   AND created_at < NOW() - INTERVAL '7 days';
   ```

---

## Email Verification Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     User Signs Up                            │
│                 (email + password)                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Supabase Creates Account                        │
│           (status: unverified)                               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│          Sends Verification Email                            │
│     (with unique confirmation link)                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
     ┌─────────────────┐   ┌─────────────────┐
     │ User Clicks Link│   │ User Tries Login│
     │   (in email)    │   │ (without verify)│
     └────────┬────────┘   └────────┬────────┘
              │                     │
              ▼                     ▼
     ┌─────────────────┐   ┌─────────────────────────┐
     │ Email Verified  │   │ Error: Verify Email     │
     │ Can Now Login   │   │ "Resend Email" Button   │
     └─────────────────┘   └─────────┬───────────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │  Clicks "Resend"    │
                           │  New Email Sent     │
                           └─────────────────────┘
```

---

## Monitoring & Analytics

### Track Email Deliverability

```sql
-- Verification success rate
SELECT
  COUNT(CASE WHEN email_confirmed_at IS NOT NULL THEN 1 END)::float /
  COUNT(*)::float * 100 as verification_rate_percentage,
  COUNT(*) as total_signups,
  COUNT(CASE WHEN email_confirmed_at IS NOT NULL THEN 1 END) as verified_users
FROM auth.users;
```

### Track Email Timing

```sql
-- Average time to verify email
SELECT
  AVG(EXTRACT(EPOCH FROM (email_confirmed_at - created_at))/3600) as avg_hours_to_verify
FROM auth.users
WHERE email_confirmed_at IS NOT NULL;
```

---

## Next Steps

### For Development:
1. ✅ Disable email confirmation (already done)
2. Focus on app features
3. Re-enable before production

### For Production:
1. ☐ Set up custom SMTP (SendGrid/Mailgun)
2. ☐ Configure SPF/DKIM records
3. ☐ Customize email templates
4. ☐ Test thoroughly
5. ☐ Enable email confirmation
6. ☐ Monitor deliverability

---

## Quick Reference

| Task | Location |
|------|----------|
| Enable/Disable Email Verification | Auth → Providers → Email → Confirm email |
| SMTP Configuration | Project Settings → Auth → SMTP Settings |
| Email Templates | Authentication → Email Templates |
| View Users | Authentication → Users |
| Check Verification Status | SQL Editor: `SELECT * FROM auth.users` |

---

## Support Resources

- [Supabase Email Auth Docs](https://supabase.com/docs/guides/auth/auth-email)
- [SMTP Providers Comparison](https://supabase.com/docs/guides/auth/auth-smtp)
- [Email Template Variables](https://supabase.com/docs/guides/auth/auth-email-templates)
