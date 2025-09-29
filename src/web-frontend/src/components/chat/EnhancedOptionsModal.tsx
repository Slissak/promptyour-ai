'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import * as Dialog from '@radix-ui/react-dialog';
import * as Select from '@radix-ui/react-select';

interface EnhancedOptionsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (theme: string, audience: string, responseStyle: string) => void;
  question: string;
}

export function EnhancedOptionsModal({ isOpen, onClose, onSubmit, question }: EnhancedOptionsModalProps) {
  const t = useTranslations();
  const [selectedTheme, setSelectedTheme] = useState('general_questions');
  const [selectedAudience, setSelectedAudience] = useState('adults');
  const [selectedResponseStyle, setSelectedResponseStyle] = useState('structured_detailed');

  const themes = [
    'academic_help',
    'creative_writing',
    'coding_programming',
    'business_professional',
    'personal_learning',
    'research_analysis',
    'problem_solving',
    'tutoring_education',
    'general_questions'
  ];

  const audiences = [
    'small_kids',
    'teenagers',
    'adults',
    'university_level',
    'professionals',
    'seniors'
  ];

  const responseStyles = [
    'paragraph_brief',
    'structured_detailed',
    'instructions_only',
    'comprehensive'
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(selectedTheme, selectedAudience, selectedResponseStyle);
  };

  return (
    <Dialog.Root open={isOpen} onOpenChange={onClose}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
        <Dialog.Content className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white rounded-lg shadow-xl p-6 w-full max-w-md z-50">
          <Dialog.Title className="text-lg font-semibold mb-4">
            ✨ Enhanced Response Options
          </Dialog.Title>

          <div className="mb-4 p-3 bg-gray-50 rounded border-l-4 border-primary-500">
            <p className="text-sm text-gray-700">
              <strong>Your Question:</strong> {question}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Theme Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('chat.choose_theme')}
              </label>
              <Select.Root value={selectedTheme} onValueChange={setSelectedTheme}>
                <Select.Trigger className="w-full flex items-center justify-between px-3 py-2 border border-gray-300 rounded-lg bg-white hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500">
                  <Select.Value />
                  <Select.Icon>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </Select.Icon>
                </Select.Trigger>
                <Select.Portal>
                  <Select.Content className="bg-white rounded-lg shadow-lg border border-gray-200 p-1 max-h-60 overflow-y-auto z-50">
                    <Select.Viewport>
                      {themes.map((theme) => (
                        <Select.Item
                          key={theme}
                          value={theme}
                          className="px-3 py-2 text-sm rounded cursor-pointer hover:bg-primary-50 focus:bg-primary-50 focus:outline-none"
                        >
                          <Select.ItemText>{t(`chat.themes.${theme}`)}</Select.ItemText>
                        </Select.Item>
                      ))}
                    </Select.Viewport>
                  </Select.Content>
                </Select.Portal>
              </Select.Root>
            </div>

            {/* Audience Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('chat.choose_audience')}
              </label>
              <Select.Root value={selectedAudience} onValueChange={setSelectedAudience}>
                <Select.Trigger className="w-full flex items-center justify-between px-3 py-2 border border-gray-300 rounded-lg bg-white hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500">
                  <Select.Value />
                  <Select.Icon>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </Select.Icon>
                </Select.Trigger>
                <Select.Portal>
                  <Select.Content className="bg-white rounded-lg shadow-lg border border-gray-200 p-1 max-h-60 overflow-y-auto z-50">
                    <Select.Viewport>
                      {audiences.map((audience) => (
                        <Select.Item
                          key={audience}
                          value={audience}
                          className="px-3 py-2 text-sm rounded cursor-pointer hover:bg-primary-50 focus:bg-primary-50 focus:outline-none"
                        >
                          <Select.ItemText>{t(`chat.audiences.${audience}`)}</Select.ItemText>
                        </Select.Item>
                      ))}
                    </Select.Viewport>
                  </Select.Content>
                </Select.Portal>
              </Select.Root>
            </div>

            {/* Response Style Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Response Style
              </label>
              <Select.Root value={selectedResponseStyle} onValueChange={setSelectedResponseStyle}>
                <Select.Trigger className="w-full flex items-center justify-between px-3 py-2 border border-gray-300 rounded-lg bg-white hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500">
                  <Select.Value />
                  <Select.Icon>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </Select.Icon>
                </Select.Trigger>
                <Select.Portal>
                  <Select.Content className="bg-white rounded-lg shadow-lg border border-gray-200 p-1 max-h-60 overflow-y-auto z-50">
                    <Select.Viewport>
                      {responseStyles.map((style) => (
                        <Select.Item
                          key={style}
                          value={style}
                          className="px-3 py-2 text-sm rounded cursor-pointer hover:bg-primary-50 focus:bg-primary-50 focus:outline-none"
                        >
                          <Select.ItemText>
                            {style === 'paragraph_brief' && 'Brief Paragraph - Concise, one paragraph response'}
                            {style === 'structured_detailed' && 'Structured & Detailed - Organized with clear sections and examples'}
                            {style === 'instructions_only' && 'Instructions Only - Direct actions without background'}
                            {style === 'comprehensive' && 'Comprehensive - Full explanation with background and reasoning'}
                          </Select.ItemText>
                        </Select.Item>
                      ))}
                    </Select.Viewport>
                  </Select.Content>
                </Select.Portal>
              </Select.Root>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex-1 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
              >
                Get Enhanced Answer
              </button>
            </div>
          </form>

          <Dialog.Close asChild>
            <button
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
              aria-label="Close"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </Dialog.Close>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}