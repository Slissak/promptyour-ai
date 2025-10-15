/**
 * Usage Tracking Types
 * For rate limiting and usage statistics
 */

export interface UserUsage {
  id: string;
  user_id: string;
  chat_count: number;
  last_reset_at: string;
  created_at: string;
  updated_at: string;
}

export interface ChatUsage {
  id: string;
  user_id: string;
  conversation_id: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface UsageLimits {
  max_chats_per_user: number;
  max_messages_per_chat: number;
  warning_threshold: number;
}

export interface UsageStatus {
  chats_used: number;
  chats_remaining: number;
  chats_limit: number;
  messages_used: number;
  messages_remaining: number;
  messages_limit: number;
  is_at_chat_limit: boolean;
  is_at_message_limit: boolean;
  is_near_chat_limit: boolean; // >= warning threshold
  is_near_message_limit: boolean; // >= warning threshold
}

export type ResponseType = 'quick_response' | 'enhanced_response';

export interface MessageWeight {
  quick_response: number;
  enhanced_response: number;
}
