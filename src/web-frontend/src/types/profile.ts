/**
 * User Profile Types
 * Matches the user_profiles table schema in Supabase
 */

export interface UserProfile {
  id: string; // UUID matching auth.users.id
  email: string | null;
  full_name: string | null;
  display_name: string | null;
  avatar_url: string | null;
  bio: string | null;

  // User preferences
  default_theme: string | null;
  default_audience: string | null;
  default_response_style: string | null;

  // Usage tracking
  total_chats: number;
  total_messages: number;

  // Metadata
  created_at: string;
  updated_at: string;
}

/**
 * Profile update data - fields that can be updated by the user
 */
export interface UserProfileUpdate {
  full_name?: string | null;
  display_name?: string | null;
  avatar_url?: string | null;
  bio?: string | null;
  default_theme?: string | null;
  default_audience?: string | null;
  default_response_style?: string | null;
}

/**
 * Profile creation data - fields required when creating a profile
 */
export interface UserProfileCreate {
  id: string;
  email: string | null;
  full_name?: string | null;
  avatar_url?: string | null;
}
