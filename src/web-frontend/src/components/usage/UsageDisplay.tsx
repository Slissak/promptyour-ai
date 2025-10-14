'use client';

import { useEffect, useState } from 'react';
import { getCurrentUsageStatus } from '@/lib/usage/actions';
import type { UsageStatus } from '@/types/usage';

interface UsageDisplayProps {
  conversationId: string;
  onLimitReached?: () => void;
}

export function UsageDisplay({ conversationId, onLimitReached }: UsageDisplayProps) {
  const [usage, setUsage] = useState<UsageStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadUsage() {
      const result = await getCurrentUsageStatus(conversationId);
      if (result.status) {
        setUsage(result.status);

        // Notify if at limit
        if (result.status.is_at_message_limit && onLimitReached) {
          onLimitReached();
        }
      }
      setIsLoading(false);
    }

    loadUsage();
  }, [conversationId, onLimitReached]);

  if (isLoading || !usage) {
    return null;
  }

  const chatPercentage = (usage.chats_used / usage.chats_limit) * 100;
  const messagePercentage = (usage.messages_used / usage.messages_limit) * 100;

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">Usage</h3>

      <div className="space-y-3">
        {/* Chats Usage */}
        <div>
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-gray-600">Chats</span>
            <span className="text-xs font-medium text-gray-900">
              {usage.chats_used} / {usage.chats_limit}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${
                usage.is_at_chat_limit
                  ? 'bg-red-500'
                  : usage.is_near_chat_limit
                  ? 'bg-yellow-500'
                  : 'bg-green-500'
              }`}
              style={{ width: `${Math.min(chatPercentage, 100)}%` }}
            />
          </div>
        </div>

        {/* Messages Usage */}
        <div>
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-gray-600">Messages (this chat)</span>
            <span className="text-xs font-medium text-gray-900">
              {usage.messages_used} / {usage.messages_limit}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${
                usage.is_at_message_limit
                  ? 'bg-red-500'
                  : usage.is_near_message_limit
                  ? 'bg-yellow-500'
                  : 'bg-green-500'
              }`}
              style={{ width: `${Math.min(messagePercentage, 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Warning Messages */}
      {usage.is_near_chat_limit && !usage.is_at_chat_limit && (
        <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-800">
          ⚠️ You're running low on chats ({usage.chats_remaining} remaining)
        </div>
      )}

      {usage.is_at_chat_limit && (
        <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-800">
          ❌ You've reached your chat limit. Upgrade to continue.
        </div>
      )}

      {usage.is_near_message_limit && !usage.is_at_message_limit && (
        <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-800">
          ⚠️ You're running low on messages ({usage.messages_remaining} remaining)
        </div>
      )}

      {usage.is_at_message_limit && (
        <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-800">
          ❌ Message limit reached. Start a new chat to continue.
        </div>
      )}

      {/* Info about message weights */}
      <div className="mt-3 pt-3 border-t border-gray-200">
        <p className="text-xs text-gray-500">
          💡 Quick responses count as 1 message, Enhanced responses count as 2
        </p>
      </div>
    </div>
  );
}
