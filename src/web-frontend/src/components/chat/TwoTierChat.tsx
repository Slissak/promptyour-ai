'use client';

import { useState, useRef, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { PromptYourAIClient } from '@shared/api/client';
import { getConversationManager } from '@shared/utils/conversation';
import type { QuickInput, QuickResponse, UserInput, ChatResponse, ChatMessage, ThemeType, AudienceType, ResponseStyle } from '@shared/types/api';
import { MessageRole } from '@shared/types/api';
import { ChatMessageDisplay } from './ChatMessageDisplay';
import { EnhancedOptionsModal } from './EnhancedOptionsModal';

interface TwoTierChatProps {
  locale: string;
}

export function TwoTierChat({ locale }: TwoTierChatProps) {
  const t = useTranslations();
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showEnhancedModal, setShowEnhancedModal] = useState(false);
  const [currentQuickResponse, setCurrentQuickResponse] = useState<QuickResponse | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [hasEnhancedResponse, setHasEnhancedResponse] = useState(false);

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

    // Add user message to conversation
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: MessageRole.USER,
      content: question,
      timestamp: new Date().toISOString()
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    conversationManagerRef.current.addUserMessage(conversationId, question);

    try {
      // Step 1: Get quick response
      const quickInput: QuickInput = {
        question,
        conversation_id: conversationId,
        message_history: conversationManagerRef.current.getMessageHistory(conversationId)
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
    setShowEnhancedModal(true);
  };

  const handleEnhancedSubmit = async (theme: string, audience: string, responseStyle: string) => {
    if (!clientRef.current || !currentQuestion) return;

    const conversationId = conversationManagerRef.current.getActiveConversation()?.metadata.id;
    if (!conversationId) return;

    setShowEnhancedModal(false);
    setIsLoading(true);

    try {
      // Step 2: Get enhanced response
      const enhancedInput: UserInput = {
        question: currentQuestion,
        theme: theme as ThemeType,
        audience: audience as AudienceType,
        response_style: responseStyle as ResponseStyle,
        conversation_id: conversationId,
        message_history: conversationManagerRef.current.getMessageHistory(conversationId)
      };

      const enhancedResponse = await clientRef.current.sendEnhancedMessage(enhancedInput);

      // Replace the quick response with enhanced response
      const enhancedMessage: ChatMessage = {
        id: (Date.now() + 2).toString(),
        role: MessageRole.ASSISTANT,
        content: enhancedResponse.content,
        timestamp: new Date().toISOString(),
        metadata: {
          type: 'enhanced',
          model: enhancedResponse.model_used,
          provider: enhancedResponse.provider,
          theme,
          audience,
          system_prompt: enhancedResponse.system_prompt
        }
      };

      // Add enhanced response as a new message (keep both quick and enhanced)
      setMessages(prev => [...prev, enhancedMessage]);
      setHasEnhancedResponse(true); // Mark that enhanced response was generated

      // Update conversation history with enhanced response
      conversationManagerRef.current.addEnhancedResponse(conversationId, enhancedResponse);

    } catch (error) {
      console.error('Failed to get enhanced response:', error);
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
            {messages.map((message) => (
              <ChatMessageDisplay
                key={message.id}
                message={message}
                onRequestEnhanced={
                  message.metadata?.type === 'quick' && currentQuickResponse && !hasEnhancedResponse
                    ? handleRequestEnhanced
                    : undefined
                }
              />
            ))}
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

      {/* Enhanced Options Modal */}
      {showEnhancedModal && (
        <EnhancedOptionsModal
          isOpen={showEnhancedModal}
          onClose={() => setShowEnhancedModal(false)}
          onSubmit={handleEnhancedSubmit}
          question={currentQuestion}
        />
      )}
    </div>
  );
}