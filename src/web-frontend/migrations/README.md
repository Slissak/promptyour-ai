# Database Migrations

This directory contains SQL migration files for setting up the Supabase database schema.

## Running Migrations

### Option 1: Supabase Dashboard (Recommended)

1. Log in to your Supabase project at https://app.supabase.com
2. Navigate to the SQL Editor (left sidebar)
3. Open each migration file in this directory in order (001, 002, 003...)
4. Copy the contents of the migration file
5. Paste into the SQL Editor
6. Click "Run" to execute the migration

### Option 2: Supabase CLI

If you have the Supabase CLI installed:

```bash
# Link your project (first time only)
supabase link --project-ref your-project-ref

# Apply migrations
supabase db push
```

## Migration Files

### 001_create_user_profiles.sql
Creates the `user_profiles` table with:
- User information (name, email, avatar, bio)
- User preferences (theme, audience, response style)
- Usage tracking (total chats, messages)
- Row Level Security (RLS) policies
- Automatic profile creation trigger
- Timestamp management

**Required for**: Profile pages to work

### 002_add_usage_functions.sql (if exists)
Additional functionality for usage tracking

### 003_create_usage_tracking.sql (if exists)
Rate limiting and usage tracking tables

## Important Notes

- **Run migrations in order** (001, 002, 003, etc.)
- **Safe to re-run**: Migrations use `IF EXISTS` checks and can be safely re-run
- **RLS enabled**: All tables have Row Level Security to protect user data
- **Auto-creation**: New user profiles are automatically created when users sign up

## Verifying Migrations

After running migrations, verify in Supabase Dashboard:

1. Go to **Table Editor**
2. Check that `user_profiles` table exists
3. Go to **SQL Editor** and run:

```sql
SELECT * FROM user_profiles LIMIT 1;
```

If you see the table structure, the migration was successful.

## Troubleshooting

### "Table already exists" error
- This is safe to ignore if re-running migrations
- Migrations use `CREATE TABLE IF NOT EXISTS`

### "Permission denied" error
- Make sure you're running migrations as the database owner
- Use the SQL Editor in Supabase Dashboard

### "Function already exists" error
- Safe to ignore
- Migrations use `CREATE OR REPLACE FUNCTION`
