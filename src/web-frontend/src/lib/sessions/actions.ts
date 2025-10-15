'use server'

import { revalidatePath } from 'next/cache';
import { createClient } from '@/lib/supabase/server';

export interface Session {
  id: string;
  user_id: string;
  created_at: string;
  updated_at: string;
  factor_id: string | null;
  aal: string | null;
  not_after: string | null;
  refreshed_at: string | null;
  user_agent: string | null;
  ip: string | null;
}

/**
 * Get all sessions for the current user
 * Note: Supabase only exposes the current session by default
 * For multiple sessions, you need Supabase Pro or custom tracking
 */
export async function getUserSessions() {
  const supabase = await createClient();

  const { data: { user }, error: authError } = await supabase.auth.getUser();

  if (authError || !user) {
    return { error: 'Not authenticated' };
  }

  // Get current session
  const { data: { session }, error: sessionError } = await supabase.auth.getSession();

  if (sessionError) {
    return { error: sessionError.message };
  }

  if (!session) {
    return { sessions: [] };
  }

  // For Supabase free tier, we can only get the current session
  // To track multiple sessions, you'd need to implement custom session tracking
  const sessions = [{
    id: session.access_token.substring(0, 8) + '...', // Shortened for display
    user_id: user.id,
    created_at: session.user?.created_at || new Date().toISOString(),
    updated_at: new Date().toISOString(),
    factor_id: null,
    aal: null,
    not_after: null,
    refreshed_at: session.user?.last_sign_in_at || null,
    user_agent: null, // Would need to be tracked separately
    ip: null, // Would need to be tracked separately
    is_current: true,
  }];

  return { sessions };
}

/**
 * Sign out from all devices
 * This invalidates all sessions for the user
 */
export async function signOutAllDevices(locale: string = 'en') {
  const supabase = await createClient();

  const { error } = await supabase.auth.signOut({ scope: 'global' });

  if (error) {
    return { error: error.message };
  }

  revalidatePath('/', 'layout');

  return {
    success: true,
    message: 'Signed out from all devices successfully',
    redirectTo: `/${locale}/login`
  };
}

/**
 * Refresh current session
 */
export async function refreshSession() {
  const supabase = await createClient();

  const { data, error } = await supabase.auth.refreshSession();

  if (error) {
    return { error: error.message };
  }

  revalidatePath('/', 'layout');

  return {
    success: true,
    session: data.session
  };
}

/**
 * Get session info for display
 */
export async function getSessionInfo() {
  const supabase = await createClient();

  const { data: { session }, error } = await supabase.auth.getSession();

  if (error || !session) {
    return { error: 'No active session' };
  }

  return {
    session: {
      created_at: session.user?.created_at,
      last_sign_in: session.user?.last_sign_in_at,
      expires_at: session.expires_at,
      // Note: Browser/device info would need to be tracked separately
      // Supabase doesn't provide this by default
    }
  };
}
