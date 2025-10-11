'use client';

import { useState, useEffect } from 'react';

interface InlineEnhancedConfigProps {
  onSubmit: (theme?: string, audience?: string, responseStyle?: string, additionalContext?: string) => void;
  onCancel: () => void;
  themes: string[];
  audiences: string[];
  responseStyles: string[];
}

export function InlineEnhancedConfig({
  onSubmit,
  onCancel,
  themes,
  audiences,
  responseStyles
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
    <div className="my-4 p-6 bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-primary-300 rounded-xl shadow-lg">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-2 flex items-center gap-2">
          ✨ Customize Enhanced Response
        </h3>
        <p className="text-sm text-gray-600">
          Add context and optionally configure theme, audience, and style
        </p>
      </div>

      {/* Additional Context Input */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Additional context or follow-up questions (optional)
        </label>
        <textarea
          value={additionalContext}
          onChange={(e) => setAdditionalContext(e.target.value)}
          placeholder="Add any additional context, constraints, or follow-up questions..."
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none bg-white"
          rows={3}
        />
      </div>

      {/* Optional Configurations */}
      <div className="space-y-3 mb-4">
        {/* Theme Option */}
        <div className="flex items-start gap-3">
          <div className="flex items-center h-10">
            <input
              type="checkbox"
              id="use-theme"
              checked={useTheme}
              onChange={(e) => handleThemeCheckboxChange(e.target.checked)}
              className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
            />
          </div>
          <div className="flex-1">
            <label htmlFor="use-theme" className="block text-sm font-medium text-gray-700 mb-1">
              Theme
            </label>
            {useTheme && (
              <select
                value={selectedTheme}
                onChange={(e) => setSelectedTheme(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white"
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
        <div className="flex items-start gap-3">
          <div className="flex items-center h-10">
            <input
              type="checkbox"
              id="use-audience"
              checked={useAudience}
              onChange={(e) => handleAudienceCheckboxChange(e.target.checked)}
              className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
            />
          </div>
          <div className="flex-1">
            <label htmlFor="use-audience" className="block text-sm font-medium text-gray-700 mb-1">
              Audience
            </label>
            {useAudience && (
              <select
                value={selectedAudience}
                onChange={(e) => setSelectedAudience(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white"
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
        <div className="flex items-start gap-3">
          <div className="flex items-center h-10">
            <input
              type="checkbox"
              id="use-style"
              checked={useResponseStyle}
              onChange={(e) => handleResponseStyleCheckboxChange(e.target.checked)}
              className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
            />
          </div>
          <div className="flex-1">
            <label htmlFor="use-style" className="block text-sm font-medium text-gray-700 mb-1">
              Response Style
            </label>
            {useResponseStyle && (
              <select
                value={selectedResponseStyle}
                onChange={(e) => setSelectedResponseStyle(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white"
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

      {/* Action Buttons */}
      <div className="flex gap-3 pt-2">
        <button
          onClick={onCancel}
          className="flex-1 px-4 py-2.5 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium"
        >
          Cancel
        </button>
        <button
          onClick={handleSubmit}
          className="flex-1 px-4 py-2.5 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors font-medium shadow-sm"
        >
          Get Enhanced Response
        </button>
      </div>
    </div>
  );
}
