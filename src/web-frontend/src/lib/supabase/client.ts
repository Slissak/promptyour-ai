import { createBrowserClient } from '@supabase/ssr'

/**
 * Create a Supabase client for use in browser (Client Components)
 * This client automatically handles cookies and sessions
 */
export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
