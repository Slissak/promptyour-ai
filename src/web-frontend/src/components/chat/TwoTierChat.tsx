'use client';

import { useState, useRef, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { PromptYourAIClient } from '@shared/api/client';
import { getConversationManager } from '@shared/utils/conversation';
import type { QuickInput, QuickResponse, UserInput, ChatResponse, ChatMessage, ThemeType, AudienceType, ResponseStyle } from '@shared/types/api';
import { MessageRole } from '@shared/types/api';
import { ChatMessageDisplay } from './ChatMessageDisplay';
import { ComparisonView } from './ComparisonView';
import { InlineEnhancedConfig } from './InlineEnhancedConfig';
import { useUserMode } from '@/hooks/useUserMode';
import { THEMES, AUDIENCES, RESPONSE_STYLES } from '@/config/generated-options';

interface TwoTierChatProps {
  locale: string;
}

export function TwoTierChat({ locale }: TwoTierChatProps) {
  const t = useTranslations();
  const { isAdvancedMode } = useUserMode();
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showInlineConfig, setShowInlineConfig] = useState(false);
  const [currentQuickResponse, setCurrentQuickResponse] = useState<QuickResponse | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [hasEnhancedResponse, setHasEnhancedResponse] = useState(false);
  const [conversationTheme, setConversationTheme] = useState<string | undefined>(undefined);
  const [conversationAudience, setConversationAudience] = useState<string | undefined>(undefined);
  const [conversationResponseStyle, setConversationResponseStyle] = useState<string | undefined>(undefined);
  const [currentQuestionHistory, setCurrentQuestionHistory] = useState<ChatMessage[]>([]);

  // Options loaded from generated config (built from YAML at build time)
  const themes = Array.from(THEMES);
  const audiences = Array.from(AUDIENCES);
  const responseStyles = Array.from(RESPONSE_STYLES);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const clientRef = useRef<PromptYourAIClient | null>(null);
  const conversationManagerRef = useRef(getConversationManager());

  // Initialize API client
  useEffect(() => {
    clientRef.current = new PromptYourAIClient({ baseURL: 'http://localhost:8001' });
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmitQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !clientRef.current) return;

    const question = input.trim();
    setCurrentQuestion(question);
    setInput('');
    setIsLoading(true);
    setHasEnhancedResponse(false); // Reset for new question

    // Create conversation if none exists
    let conversationId = conversationManagerRef.current.getActiveConversation()?.metadata.id;
    if (!conversationId) {
      conversationId = conversationManagerRef.current.createConversation();
      conversationManagerRef.current.setActiveConversation(conversationId);
    }

    // Get message history BEFORE adding current message
    // This ensures the current question is NOT included in the history
    const previousHistory = conversationManagerRef.current.getMessageHistory(conversationId);

    // Store this history so enhanced response can use the same context
    setCurrentQuestionHistory(previousHistory);

    // Add user message to UI
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: MessageRole.USER,
      content: question,
      timestamp: new Date().toISOString()
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);

    try {
      // Step 1: Get quick response (with previous history only, not including current question)
      const quickInput: QuickInput = {
        question,
        conversation_id: conversationId,
        message_history: previousHistory
      };

      const quickResponse = await clientRef.current.sendQuickMessage(quickInput);

      // Display quick response
      const quickMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: MessageRole.ASSISTANT,
        content: quickResponse.content,
        timestamp: new Date().toISOString(),
        metadata: {
          type: 'quick',
          model: quickResponse.model_used,
          provider: quickResponse.provider,
          system_prompt: quickResponse.system_prompt
        }
      };

      setMessages(prev => [...prev, quickMessage]);

      // Now add both user message and quick response to conversation history
      conversationManagerRef.current.addUserMessage(conversationId, question);
      conversationManagerRef.current.addQuickResponse(conversationId, quickResponse);
      setCurrentQuickResponse(quickResponse);

    } catch (error) {
      console.error('Failed to get quick response:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: MessageRole.ASSISTANT,
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
        metadata: {
          type: 'error'
        }
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRequestEnhanced = () => {
    setShowInlineConfig(true);
  };

  const handleInlineConfigCancel = () => {
    setShowInlineConfig(false);
  };

  const handleEnhancedSubmit = async (theme?: string, audience?: string, responseStyle?: string, additionalContext?: string) => {
    if (!clientRef.current || !currentQuestion) return;

    const conversationId = conversationManagerRef.current.getActiveConversation()?.metadata.id;
    if (!conversationId) return;

    setShowInlineConfig(false);
    setIsLoading(true);

    // Save conversation preferences on first enhanced request, or use existing ones
    const finalTheme = theme || conversationTheme;
    const finalAudience = audience || conversationAudience;
    const finalResponseStyle = responseStyle || conversationResponseStyle;

    // Save preferences for future requests in this conversation
    if (theme) setConversationTheme(theme);
    if (audience) setConversationAudience(audience);
    if (responseStyle) setConversationResponseStyle(responseStyle);

    try {
      // Combine question with additional context if provided
      const fullQuestion = additionalContext
        ? `${currentQuestion}\n\nAdditional context: ${additionalContext}`
        : currentQuestion;

      // Step 2: Get enhanced response
      // Use the SAME message history that was used for quick response
      // (i.e., history BEFORE the current question)
      const enhancedInput: UserInput = {
        question: fullQuestion,
        theme: finalTheme as ThemeType | undefined,
        audience: finalAudience as AudienceType | undefined,
        response_style: finalResponseStyle as ResponseStyle | undefined,
        conversation_id: conversationId,
        message_history: currentQuestionHistory
      };

      const enhancedResponse = await clientRef.current.sendEnhancedMessage(enhancedInput);

      // Debug: Log the enhanced response to check raw_response
      console.log('Enhanced Response received:', {
        hasRawResponse: !!enhancedResponse.raw_response,
        rawResponseLength: enhancedResponse.raw_response?.length || 0,
        rawResponsePreview: enhancedResponse.raw_response?.substring(0, 100) || 'EMPTY',
        enhancedContentLength: enhancedResponse.content?.length || 0,
        mode: isAdvancedMode ? 'advanced' : 'regular'
      });

      if (isAdvancedMode) {
        // ADVANCED MODE: Show comparison view (RAW vs Enhanced)
        const comparisonMessage: ChatMessage = {
          id: (Date.now() + 2).toString(),
          role: MessageRole.ASSISTANT,
          content: 'Comparison View', // Placeholder, actual content rendered by ComparisonView
          timestamp: new Date().toISOString(),
          metadata: {
            type: 'comparison',
            theme,
            audience,
            // Create a pseudo QuickResponse for the RAW response
            quickResponse: {
              content: enhancedResponse.raw_response || '',
              model_used: enhancedResponse.model_used,
              provider: enhancedResponse.provider,
              message_id: enhancedResponse.message_id + '_raw',
              cost: 0,
              response_time_ms: 0,
              system_prompt: ''  // Empty - completely RAW
            },
            enhancedResponse: enhancedResponse
          }
        };

        // Add comparison message (keep quick response visible)
        setMessages(prev => [...prev, comparisonMessage]);
      } else {
        // REGULAR MODE: Add enhanced response as a new message
        const enhancedMessage: ChatMessage = {
          id: (Date.now() + 2).toString(),
          role: MessageRole.ASSISTANT,
          content: enhancedResponse.content,
          timestamp: new Date().toISOString(),
          metadata: {
            type: 'enhanced',
            model: enhancedResponse.model_used,
            provider: enhancedResponse.provider,
            system_prompt: enhancedResponse.system_prompt,
            theme,
            audience
          }
        };

        setMessages(prev => [...prev, enhancedMessage]);
      }

      setHasEnhancedResponse(true); // Mark that enhanced response was generated

      // Update conversation history with enhanced response
      conversationManagerRef.current.addEnhancedResponse(conversationId, enhancedResponse);

    } catch (error: any) {
      console.error('Failed to get enhanced response:', {
        message: error?.message,
        response: error?.response?.data,
        status: error?.response?.status,
        error: error
      });

      // Show error message to user
      const errorMessage: ChatMessage = {
        id: (Date.now() + 3).toString(),
        role: MessageRole.ASSISTANT,
        content: `Sorry, I encountered an error getting the enhanced response: ${error?.response?.data?.detail || error?.message || 'Unknown error'}`,
        timestamp: new Date().toISOString(),
        metadata: {
          type: 'error'
        }
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setCurrentQuickResponse(null);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setCurrentQuickResponse(null);
    setCurrentQuestion('');
    setHasEnhancedResponse(false);
    setCurrentQuestionHistory([]); // Clear message history for new conversation
    // Reset conversation preferences for new conversation
    setConversationTheme(undefined);
    setConversationAudience(undefined);
    setConversationResponseStyle(undefined);
    // Clear all previous conversations and start fresh
    conversationManagerRef.current.clearAllConversations();
    const newConversationId = conversationManagerRef.current.createConversation();
    conversationManagerRef.current.setActiveConversation(newConversationId);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-16">
            <div className="text-6xl mb-4">💬</div>
            <h3 className="text-lg font-medium mb-2">Start a conversation</h3>
            <p className="text-sm">Ask any question to get started. You'll get a quick answer first, then can request a more detailed response.</p>
          </div>
        ) : (
          <>
            {messages.map((message) => {
              // Render comparison view for comparison messages
              if (message.metadata?.type === 'comparison' && message.metadata.quickResponse && message.metadata.enhancedResponse) {
                return (
                  <ComparisonView
                    key={message.id}
                    quickResponse={{
                      content: message.metadata.quickResponse.content,
                      model: message.metadata.quickResponse.model_used,
                      provider: message.metadata.quickResponse.provider,
                      systemPrompt: message.metadata.quickResponse.system_prompt
                    }}
                    enhancedResponse={{
                      content: message.metadata.enhancedResponse.content,
                      model: message.metadata.enhancedResponse.model_used,
                      provider: message.metadata.enhancedResponse.provider,
                      systemPrompt: message.metadata.enhancedResponse.system_prompt,
                      theme: message.metadata.theme,
                      audience: message.metadata.audience
                    }}
                  />
                );
              }

              // Render regular message display for other message types
              return (
                <ChatMessageDisplay
                  key={message.id}
                  message={message}
                  onRequestEnhanced={
                    message.metadata?.type === 'quick' && currentQuickResponse && !hasEnhancedResponse
                      ? handleRequestEnhanced
                      : undefined
                  }
                />
              );
            })}

            {/* Inline Enhanced Configuration */}
            {showInlineConfig && (
              <InlineEnhancedConfig
                onSubmit={handleEnhancedSubmit}
                onCancel={handleInlineConfigCancel}
                themes={themes}
                audiences={audiences}
                responseStyles={responseStyles}
                isFirstEnhancedRequest={!conversationTheme}
              />
            )}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg p-3 max-w-xs animate-pulse">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t bg-gray-50 p-4">
        <div className="flex gap-2 mb-2">
          <button
            onClick={handleNewChat}
            className="text-sm text-gray-600 hover:text-gray-800 px-3 py-1 rounded border border-gray-300 hover:bg-white"
            disabled={isLoading}
          >
            {t('common.new_chat')}
          </button>
        </div>

        <form onSubmit={handleSubmitQuestion} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={t('chat.placeholder')}
            className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="bg-primary-500 hover:bg-primary-600 disabled:bg-gray-300 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            {t('common.send')}
          </button>
        </form>
      </div>

    </div>
  );
}