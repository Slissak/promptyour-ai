# Database Migrations

This directory contains SQL migration files for the Supabase database.

## Running Migrations

### Option 1: Supabase Dashboard (Recommended)

1. Go to your [Supabase Dashboard](https://app.supabase.com/)
2. Select your project
3. Navigate to **SQL Editor**
4. Click **New query**
5. Copy and paste the contents of each migration file in order:
   - `001_create_user_profiles.sql`
   - `002_add_usage_functions.sql`
6. Click **Run** to execute each migration

### Option 2: Supabase CLI

If you have the Supabase CLI installed:

```bash
# Run a specific migration
supabase db execute --file migrations/001_create_user_profiles.sql

# Or run all migrations in order
supabase db execute --file migrations/001_create_user_profiles.sql
supabase db execute --file migrations/002_add_usage_functions.sql
```

### Option 3: psql Command Line

If you have PostgreSQL client installed:

```bash
# Connect to your database
psql "postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres"

# Run migrations
\i migrations/001_create_user_profiles.sql
\i migrations/002_add_usage_functions.sql
```

## Migration Files

### 001_create_user_profiles.sql
Creates the `user_profiles` table with:
- Basic profile information (name, bio, avatar)
- User preferences (theme, audience, response style)
- Usage tracking (total chats, total messages)
- Row Level Security (RLS) policies
- Automatic profile creation trigger on user signup
- Auto-update `updated_at` trigger

### 002_add_usage_functions.sql
Creates database functions for tracking usage:
- `increment_chat_count(user_id)` - Increment total chats
- `increment_message_count(user_id, count_value)` - Increment total messages

## Verification

After running migrations, verify they worked correctly:

```sql
-- Check if user_profiles table exists
SELECT * FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name = 'user_profiles';

-- Check if functions exist
SELECT routine_name
FROM information_schema.routines
WHERE routine_type = 'FUNCTION'
AND specific_schema = 'public'
AND routine_name LIKE 'increment_%';

-- Check if RLS is enabled
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
AND tablename = 'user_profiles';
```

## Rollback

If you need to rollback these migrations:

```sql
-- Drop functions
DROP FUNCTION IF EXISTS increment_chat_count(UUID);
DROP FUNCTION IF EXISTS increment_message_count(UUID, INT);

-- Drop triggers
DROP TRIGGER IF EXISTS on_user_profile_updated ON public.user_profiles;
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Drop functions used by triggers
DROP FUNCTION IF EXISTS public.handle_updated_at();
DROP FUNCTION IF EXISTS public.handle_new_user();

-- Drop table (WARNING: This will delete all user profile data!)
DROP TABLE IF EXISTS public.user_profiles CASCADE;
```

## Notes

- Migrations are designed to be idempotent - you can run them multiple times safely
- The auto-profile creation trigger will create profiles for new users automatically
- Existing users may need to have profiles created manually or via the `ensureUserProfile` action
- RLS policies ensure users can only access their own profile data
