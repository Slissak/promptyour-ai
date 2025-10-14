-- Migration: Add usage tracking functions
-- Description: Functions to increment chat and message counts for users
-- Date: 2025-01-14

-- Function to increment chat count
CREATE OR REPLACE FUNCTION increment_chat_count(user_id UUID)
RETURNS VOID AS $$
BEGIN
  UPDATE public.user_profiles
  SET total_chats = total_chats + 1
  WHERE id = user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to increment message count
CREATE OR REPLACE FUNCTION increment_message_count(user_id UUID, count_value INT DEFAULT 1)
RETURNS VOID AS $$
BEGIN
  UPDATE public.user_profiles
  SET total_messages = total_messages + count_value
  WHERE id = user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permissions to authenticated users
GRANT EXECUTE ON FUNCTION increment_chat_count(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION increment_message_count(UUID, INT) TO authenticated;
