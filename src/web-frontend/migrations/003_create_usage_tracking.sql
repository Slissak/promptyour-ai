-- Migration: Create usage tracking tables for rate limiting
-- Description: Tracks chat and message usage per user for rate limiting
-- Date: 2025-01-14

-- User usage tracking table
CREATE TABLE IF NOT EXISTS public.user_usage (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  chat_count INT DEFAULT 0,
  last_reset_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id)
);

-- Chat usage tracking table
CREATE TABLE IF NOT EXISTS public.chat_usage (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  conversation_id TEXT NOT NULL,
  message_count INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, conversation_id)
);

-- Enable Row Level Security
ALTER TABLE public.user_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_usage ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own usage" ON public.user_usage;
DROP POLICY IF EXISTS "Users can update own usage" ON public.user_usage;
DROP POLICY IF EXISTS "Users can insert own usage" ON public.user_usage;
DROP POLICY IF EXISTS "Users can view own chat usage" ON public.chat_usage;
DROP POLICY IF EXISTS "Users can update own chat usage" ON public.chat_usage;
DROP POLICY IF EXISTS "Users can insert own chat usage" ON public.chat_usage;

-- RLS Policies for user_usage
CREATE POLICY "Users can view own usage"
  ON public.user_usage FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can update own usage"
  ON public.user_usage FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own usage"
  ON public.user_usage FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- RLS Policies for chat_usage
CREATE POLICY "Users can view own chat usage"
  ON public.chat_usage FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can update own chat usage"
  ON public.chat_usage FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own chat usage"
  ON public.chat_usage FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_usage_user_id ON public.user_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_usage_user_id ON public.chat_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_usage_conversation ON public.chat_usage(conversation_id);
CREATE INDEX IF NOT EXISTS idx_chat_usage_user_conversation ON public.chat_usage(user_id, conversation_id);

-- Function to increment chat count for a user
CREATE OR REPLACE FUNCTION increment_user_chat_count(p_user_id UUID)
RETURNS VOID AS $$
BEGIN
  INSERT INTO public.user_usage (user_id, chat_count)
  VALUES (p_user_id, 1)
  ON CONFLICT (user_id)
  DO UPDATE SET
    chat_count = public.user_usage.chat_count + 1,
    updated_at = NOW();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to increment message count for a chat
CREATE OR REPLACE FUNCTION increment_chat_message_count(
  p_user_id UUID,
  p_conversation_id TEXT,
  p_count INT DEFAULT 1
)
RETURNS VOID AS $$
BEGIN
  INSERT INTO public.chat_usage (user_id, conversation_id, message_count)
  VALUES (p_user_id, p_conversation_id, p_count)
  ON CONFLICT (user_id, conversation_id)
  DO UPDATE SET
    message_count = public.chat_usage.message_count + p_count,
    updated_at = NOW();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get user's current usage
CREATE OR REPLACE FUNCTION get_user_usage(p_user_id UUID)
RETURNS TABLE (
  chat_count INT,
  last_reset_at TIMESTAMPTZ
) AS $$
BEGIN
  RETURN QUERY
  SELECT u.chat_count, u.last_reset_at
  FROM public.user_usage u
  WHERE u.user_id = p_user_id;

  -- If no record exists, return defaults
  IF NOT FOUND THEN
    RETURN QUERY SELECT 0 AS chat_count, NOW() AS last_reset_at;
  END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get chat's current usage
CREATE OR REPLACE FUNCTION get_chat_usage(
  p_user_id UUID,
  p_conversation_id TEXT
)
RETURNS TABLE (
  message_count INT
) AS $$
BEGIN
  RETURN QUERY
  SELECT c.message_count
  FROM public.chat_usage c
  WHERE c.user_id = p_user_id
    AND c.conversation_id = p_conversation_id;

  -- If no record exists, return default
  IF NOT FOUND THEN
    RETURN QUERY SELECT 0 AS message_count;
  END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to reset user usage (for periodic resets)
CREATE OR REPLACE FUNCTION reset_user_usage(p_user_id UUID)
RETURNS VOID AS $$
BEGIN
  UPDATE public.user_usage
  SET
    chat_count = 0,
    last_reset_at = NOW(),
    updated_at = NOW()
  WHERE user_id = p_user_id;

  -- Also delete all chat usage records for this user
  DELETE FROM public.chat_usage
  WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION increment_user_chat_count(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION increment_chat_message_count(UUID, TEXT, INT) TO authenticated;
GRANT EXECUTE ON FUNCTION get_user_usage(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION get_chat_usage(UUID, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION reset_user_usage(UUID) TO authenticated;
