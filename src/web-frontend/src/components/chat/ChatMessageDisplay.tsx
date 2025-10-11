'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import ReactMarkdown from 'react-markdown';
import type { ChatMessage } from '@shared/types/api';
import { useUserMode } from '@/hooks/useUserMode';

interface ChatMessageDisplayProps {
  message: ChatMessage;
  onRequestEnhanced?: () => void;
}

export function ChatMessageDisplay({ message, onRequestEnhanced }: ChatMessageDisplayProps) {
  const t = useTranslations();
  const { isAdvancedMode } = useUserMode();
  const [showSystemPrompt, setShowSystemPrompt] = useState(false);

  const isUser = message.role === 'user';
  const isQuick = message.metadata?.type === 'quick';
  const isEnhanced = message.metadata?.type === 'enhanced';
  const isError = message.metadata?.type === 'error';
  const hasSystemPrompt = message.metadata?.system_prompt;

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-2xl ${isUser ? 'ml-4' : 'mr-4'}`}>
        {/* Message Bubble */}
        <div
          className={`rounded-lg p-4 ${
            isUser
              ? 'bg-primary-500 text-white'
              : isError
              ? 'bg-red-100 text-red-800'
              : isQuick
              ? 'bg-yellow-50 border border-yellow-200'
              : 'bg-gray-100 text-gray-900'
          }`}
        >
          {/* Quick Response Header */}
          {isQuick && (
            <div className="flex items-center gap-2 mb-2 text-sm text-yellow-700">
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-yellow-100">
                ⚡ Quick Answer
              </span>
            </div>
          )}

          {/* Enhanced Response Header */}
          {isEnhanced && (
            <div className="flex items-center gap-2 mb-2 text-sm text-gray-600">
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-primary-100 text-primary-700">
                ✨ Enhanced Answer
              </span>
              {message.metadata?.theme && (
                <span className="text-xs text-gray-500">
                  {message.metadata.theme} • {message.metadata.audience}
                </span>
              )}
            </div>
          )}

          {/* Message Content */}
          <div className={`prose prose-sm max-w-none ${isUser ? 'prose-invert' : ''}`}>
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>

          {/* System Prompt Section - Only in Advanced Mode */}
          {!isUser && hasSystemPrompt && isAdvancedMode && (
            <div className="mt-3 border-t border-gray-200 pt-2">
              <button
                onClick={() => setShowSystemPrompt(!showSystemPrompt)}
                className="flex items-center gap-1 text-xs text-gray-600 hover:text-gray-800 transition-colors"
              >
                <span className={`transform transition-transform ${showSystemPrompt ? 'rotate-90' : ''}`}>▶</span>
                <span>{showSystemPrompt ? 'Hide' : 'Show'} System Prompt</span>
              </button>
              {showSystemPrompt && (
                <div className="mt-2 p-2 bg-gray-50 rounded text-xs font-mono text-gray-700 whitespace-pre-wrap max-h-60 overflow-y-auto">
                  {message.metadata.system_prompt}
                </div>
              )}
            </div>
          )}

          {/* Model Info */}
          {!isUser && message.metadata?.model && (
            <div className="mt-2 text-xs opacity-70">
              {message.metadata.model} via {message.metadata.provider}
            </div>
          )}
        </div>

        {/* Quick Response Actions */}
        {isQuick && onRequestEnhanced && (
          <div className="mt-2 flex justify-center">
            <button
              onClick={onRequestEnhanced}
              className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-primary-600 bg-white border border-primary-200 rounded-lg hover:bg-primary-50 transition-colors"
            >
              <span>✨</span>
              Get Enhanced Response
            </button>
          </div>
        )}

        {/* Timestamp */}
        <div className={`text-xs text-gray-500 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
          {message.timestamp ? new Date(message.timestamp).toLocaleTimeString() : ''}
        </div>
      </div>
    </div>
  );
}