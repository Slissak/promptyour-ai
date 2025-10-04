'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';

interface ComparisonViewProps {
  quickResponse: {
    content: string;
    model: string;
    provider: string;
    systemPrompt: string;
  };
  enhancedResponse: {
    content: string;
    model: string;
    provider: string;
    systemPrompt: string;
    theme?: string;
    audience?: string;
  };
}

export function ComparisonView({ quickResponse, enhancedResponse }: ComparisonViewProps) {
  const [showQuickPrompt, setShowQuickPrompt] = useState(true);
  const [showEnhancedPrompt, setShowEnhancedPrompt] = useState(true);

  return (
    <div className="w-full my-4 border-2 border-gray-300 rounded-lg p-4 bg-gradient-to-r from-red-50 via-gray-50 to-green-50">
      {/* Comparison Header */}
      <div className="text-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-1">
          📊 Response Comparison
        </h3>
        <p className="text-sm text-gray-600">
          RAW model output vs Enhanced prompt engineering
        </p>
      </div>

      {/* Two-Column Layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

        {/* Left Column - RAW Response */}
        <div className="bg-white rounded-lg border-2 border-red-300 p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
                🔴 RAW Response (No Prompt Engineering)
              </span>
            </div>
          </div>

          {/* RAW System Prompt */}
          <div className="mb-4">
            <button
              onClick={() => setShowQuickPrompt(!showQuickPrompt)}
              className="flex items-center gap-1 text-sm font-medium text-gray-700 hover:text-gray-900 mb-2"
            >
              <span className={`transform transition-transform ${showQuickPrompt ? 'rotate-90' : ''}`}>▶</span>
              <span>System Prompt (Empty - RAW)</span>
            </button>
            {showQuickPrompt && (
              <div className="p-3 bg-red-50 rounded border border-red-200 text-xs font-mono text-gray-700">
                {quickResponse.systemPrompt || <span className="text-gray-400 italic">No system prompt - completely RAW</span>}
              </div>
            )}
          </div>

          {/* RAW Response Content */}
          <div className="border-t border-gray-200 pt-3">
            <h4 className="text-xs font-semibold text-gray-600 mb-2">MODEL RESPONSE (No guidance):</h4>
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown>{quickResponse.content}</ReactMarkdown>
            </div>
            <div className="mt-3 text-xs text-gray-500">
              {quickResponse.model} via {quickResponse.provider}
            </div>
          </div>
        </div>

        {/* Right Column - Enhanced Response */}
        <div className="bg-white rounded-lg border-2 border-green-300 p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                ✨ Enhanced (With Prompt Engineering)
              </span>
            </div>
          </div>

          {/* Enhanced System Prompt */}
          <div className="mb-4">
            <button
              onClick={() => setShowEnhancedPrompt(!showEnhancedPrompt)}
              className="flex items-center gap-1 text-sm font-medium text-gray-700 hover:text-gray-900 mb-2"
            >
              <span className={`transform transition-transform ${showEnhancedPrompt ? 'rotate-90' : ''}`}>▶</span>
              <span>System Prompt (Enhanced)</span>
            </button>
            {showEnhancedPrompt && (
              <div className="p-3 bg-green-50 rounded border border-green-200 text-xs font-mono text-gray-700 whitespace-pre-wrap max-h-60 overflow-y-auto">
                {enhancedResponse.systemPrompt}
              </div>
            )}
            {enhancedResponse.theme && (
              <div className="mt-2 text-xs text-gray-600">
                <span className="font-medium">Theme:</span> {enhancedResponse.theme} • <span className="font-medium">Audience:</span> {enhancedResponse.audience}
              </div>
            )}
          </div>

          {/* Enhanced Response Content */}
          <div className="border-t border-gray-200 pt-3">
            <h4 className="text-xs font-semibold text-gray-600 mb-2">MODEL RESPONSE (With guidance):</h4>
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown>{enhancedResponse.content}</ReactMarkdown>
            </div>
            <div className="mt-3 text-xs text-gray-500">
              {enhancedResponse.model} via {enhancedResponse.provider}
            </div>
          </div>
        </div>

      </div>

      {/* Legend */}
      <div className="mt-4 pt-3 border-t border-gray-300 text-xs text-gray-600 text-center">
        <span className="font-medium">💡 Tip:</span> The RAW response has NO system prompt or guidance - just the model's natural answer. Compare it to the enhanced version to see the power of prompt engineering!
      </div>
    </div>
  );
}
