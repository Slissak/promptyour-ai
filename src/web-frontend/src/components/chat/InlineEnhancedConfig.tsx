'use client';

import { useState, useEffect } from 'react';

interface InlineEnhancedConfigProps {
  onSubmit: (theme?: string, audience?: string, responseStyle?: string, additionalContext?: string) => void;
  onCancel: () => void;
  themes: string[];
  audiences: string[];
  responseStyles: string[];
  isFirstEnhancedRequest?: boolean;
}

export function InlineEnhancedConfig({
  onSubmit,
  onCancel,
  themes,
  audiences,
  responseStyles,
  isFirstEnhancedRequest = true
}: InlineEnhancedConfigProps) {
  const [additionalContext, setAdditionalContext] = useState('');
  const [useTheme, setUseTheme] = useState(false);
  const [useAudience, setUseAudience] = useState(false);
  const [useResponseStyle, setUseResponseStyle] = useState(false);
  const [selectedTheme, setSelectedTheme] = useState('');
  const [selectedAudience, setSelectedAudience] = useState('');
  const [selectedResponseStyle, setSelectedResponseStyle] = useState('');

  const handleThemeCheckboxChange = (checked: boolean) => {
    setUseTheme(checked);
    if (checked && themes.length > 0) {
      setSelectedTheme(themes[0]);
    }
  };

  const handleAudienceCheckboxChange = (checked: boolean) => {
    setUseAudience(checked);
    if (checked && audiences.length > 0) {
      setSelectedAudience(audiences[0]);
    }
  };

  const handleResponseStyleCheckboxChange = (checked: boolean) => {
    setUseResponseStyle(checked);
    if (checked && responseStyles.length > 0) {
      setSelectedResponseStyle(responseStyles[0]);
    }
  };

  const handleSubmit = () => {
    onSubmit(
      useTheme ? selectedTheme : undefined,
      useAudience ? selectedAudience : undefined,
      useResponseStyle ? selectedResponseStyle : undefined,
      additionalContext || undefined
    );
  };

  return (
    <div className="my-2 p-3 bg-gradient-to-br from-blue-50 to-indigo-50 border border-primary-300 rounded-lg shadow">
      <div className="mb-2">
        <h3 className="text-sm font-semibold text-gray-800 mb-1 flex items-center gap-1">
          ✨ Customize Enhanced Response
        </h3>
      </div>

      {/* Additional Context Input */}
      <div className="mb-2">
        <label className="block text-xs font-medium text-gray-700 mb-1">
          Additional context (optional)
        </label>
        <textarea
          value={additionalContext}
          onChange={(e) => setAdditionalContext(e.target.value)}
          placeholder="Add context or follow-up questions..."
          className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-primary-500 focus:border-transparent resize-none bg-white"
          rows={2}
        />
      </div>

      {/* Optional Configurations - Only show on first enhanced request */}
      {isFirstEnhancedRequest && (
        <div className="space-y-1.5 mb-2">
          {/* Theme Option */}
          <div className="flex items-start gap-2">
            <div className="flex items-center h-7">
              <input
                type="checkbox"
                id="use-theme"
                checked={useTheme}
                onChange={(e) => handleThemeCheckboxChange(e.target.checked)}
                className="w-3.5 h-3.5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
            </div>
            <div className="flex-1">
              <label htmlFor="use-theme" className="block text-xs font-medium text-gray-700 mb-0.5">
                Theme
              </label>
              {useTheme && (
                <select
                  value={selectedTheme}
                  onChange={(e) => setSelectedTheme(e.target.value)}
                  className="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-primary-500 focus:border-transparent bg-white"
                >
                  {themes.map((theme) => (
                    <option key={theme} value={theme}>
                      {theme.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                    </option>
                  ))}
                </select>
              )}
            </div>
          </div>

          {/* Audience Option */}
          <div className="flex items-start gap-2">
            <div className="flex items-center h-7">
              <input
                type="checkbox"
                id="use-audience"
                checked={useAudience}
                onChange={(e) => handleAudienceCheckboxChange(e.target.checked)}
                className="w-3.5 h-3.5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
            </div>
            <div className="flex-1">
              <label htmlFor="use-audience" className="block text-xs font-medium text-gray-700 mb-0.5">
                Audience
              </label>
              {useAudience && (
                <select
                  value={selectedAudience}
                  onChange={(e) => setSelectedAudience(e.target.value)}
                  className="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-primary-500 focus:border-transparent bg-white"
                >
                  {audiences.map((audience) => (
                    <option key={audience} value={audience}>
                      {audience.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                    </option>
                  ))}
                </select>
              )}
            </div>
          </div>

          {/* Response Style Option */}
          <div className="flex items-start gap-2">
            <div className="flex items-center h-7">
              <input
                type="checkbox"
                id="use-style"
                checked={useResponseStyle}
                onChange={(e) => handleResponseStyleCheckboxChange(e.target.checked)}
                className="w-3.5 h-3.5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
            </div>
            <div className="flex-1">
              <label htmlFor="use-style" className="block text-xs font-medium text-gray-700 mb-0.5">
                Response Style
              </label>
              {useResponseStyle && (
                <select
                  value={selectedResponseStyle}
                  onChange={(e) => setSelectedResponseStyle(e.target.value)}
                  className="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-primary-500 focus:border-transparent bg-white"
                >
                  {responseStyles.map((style) => (
                    <option key={style} value={style}>
                      {style.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                    </option>
                  ))}
                </select>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-2 pt-1">
        <button
          onClick={onCancel}
          className="flex-1 px-3 py-1.5 text-sm text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50 transition-colors font-medium"
        >
          Cancel
        </button>
        <button
          onClick={handleSubmit}
          className="flex-1 px-3 py-1.5 text-sm bg-primary-500 text-white rounded hover:bg-primary-600 transition-colors font-medium shadow-sm"
        >
          Get Enhanced Response
        </button>
      </div>
    </div>
  );
}
