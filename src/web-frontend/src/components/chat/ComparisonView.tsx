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
    <div className="w-full my-4 border-2 border-primary-200 rounded-lg p-4 bg-gradient-to-r from-yellow-50 to-blue-50">
      {/* Comparison Header */}
      <div className="text-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-1">
          📊 Response Comparison
        </h3>
        <p className="text-sm text-gray-600">
          See the difference between basic and enhanced prompt engineering
        </p>
      </div>

      {/* Two-Column Layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

        {/* Left Column - Quick Response */}
        <div className="bg-white rounded-lg border-2 border-yellow-300 p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
                ⚡ Quick Response
              </span>
            </div>
          </div>

          {/* Quick System Prompt */}
          <div className="mb-4">
            <button
              onClick={() => setShowQuickPrompt(!showQuickPrompt)}
              className="flex items-center gap-1 text-sm font-medium text-gray-700 hover:text-gray-900 mb-2"
            >
              <span className={`transform transition-transform ${showQuickPrompt ? 'rotate-90' : ''}`}>▶</span>
              <span>System Prompt (Basic)</span>
            </button>
            {showQuickPrompt && (
              <div className="p-3 bg-yellow-50 rounded border border-yellow-200 text-xs font-mono text-gray-700 whitespace-pre-wrap max-h-60 overflow-y-auto">
                {quickResponse.systemPrompt}
              </div>
            )}
          </div>

          {/* Quick Response Content */}
          <div className="border-t border-gray-200 pt-3">
            <h4 className="text-xs font-semibold text-gray-600 mb-2">MODEL RESPONSE:</h4>
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown>{quickResponse.content}</ReactMarkdown>
            </div>
            <div className="mt-3 text-xs text-gray-500">
              {quickResponse.model} via {quickResponse.provider}
            </div>
          </div>
        </div>

        {/* Right Column - Enhanced Response */}
        <div className="bg-white rounded-lg border-2 border-primary-300 p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800">
                ✨ Enhanced Response
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
              <div className="p-3 bg-primary-50 rounded border border-primary-200 text-xs font-mono text-gray-700 whitespace-pre-wrap max-h-60 overflow-y-auto">
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
            <h4 className="text-xs font-semibold text-gray-600 mb-2">MODEL RESPONSE:</h4>
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
        <span className="font-medium">💡 Tip:</span> Compare the system prompts to see how enhanced prompt engineering shapes the AI's response
      </div>
    </div>
  );
}
