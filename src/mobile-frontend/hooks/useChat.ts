/**
 * useChat Hook
 * Custom hook for managing chat functionality
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useChatStore } from '../store/chatStore';
import { useConfigStore } from '../store/configStore';
import { useUserStore } from '../store/userStore';
import { apiService } from '../services/api';
import { createWebSocketService, WebSocketService } from '../services/websocket';
import { ChatMode, UserInput, QuickInput, RawInput } from '../types/api';
import { storageService } from '../services/storage';

export const useChat = () => {
  const chatStore = useChatStore();
  const configStore = useConfigStore();
  const { userId } = useUserStore();

  const wsRef = useRef<WebSocketService | null>(null);
  const [useWebSocket, setUseWebSocket] = useState(true);

  // Initialize WebSocket if needed
  useEffect(() => {
    if (useWebSocket && userId && !wsRef.current) {
      wsRef.current = createWebSocketService(userId);

      // Set up WebSocket event handlers
      wsRef.current.onConnect(() => {
        chatStore.setConnected(true);
      });

      wsRef.current.onDisconnect(() => {
        chatStore.setConnected(false);
      });

      wsRef.current.onError((error) => {
        console.error('[useChat] WebSocket error:', error);
        chatStore.setError(error.message);
      });

      wsRef.current.on('processing_update', (message: any) => {
        chatStore.setProcessingStatus(message.status);
      });

      // Connect
      wsRef.current
        .connect(chatStore.conversationId || undefined)
        .catch((error) => {
          console.error('[useChat] Failed to connect WebSocket:', error);
          // Fall back to REST API
          setUseWebSocket(false);
        });
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.disconnect();
        wsRef.current = null;
      }
    };
  }, [useWebSocket, userId]);

  // Load chat mode from storage
  useEffect(() => {
    const loadChatMode = async () => {
      const savedMode = await storageService.getChatMode();
      if (savedMode) {
        chatStore.setChatMode(savedMode as ChatMode);
      }
    };
    loadChatMode();
  }, []);

  // Save chat mode to storage when it changes
  useEffect(() => {
    storageService.setChatMode(chatStore.chatMode);
  }, [chatStore.chatMode]);

  /**
   * Send a chat message
   */
  const sendMessage = useCallback(
    async (question: string) => {
      if (!question.trim()) {
        return;
      }

      try {
        chatStore.setLoading(true);
        chatStore.addUserMessage(question);

        const { chatMode } = chatStore;
        const messageHistory = chatStore.messages.map((msg) => ({
          role: msg.role,
          content: msg.content,
          timestamp: msg.timestamp,
          model: msg.model,
          provider: msg.provider,
        }));

        let response;

        if (chatMode === ChatMode.QUICK) {
          // Quick mode
          const input: QuickInput = {
            question,
            conversation_id: chatStore.conversationId || undefined,
            message_history: messageHistory,
          };

          if (useWebSocket && wsRef.current?.isConnected()) {
            response = await wsRef.current.sendChatMessage(ChatMode.QUICK, input);
          } else {
            response = await apiService.sendQuickMessage(input);
          }
        } else if (chatMode === ChatMode.RAW) {
          // Raw mode
          const input: RawInput = {
            question,
            conversation_id: chatStore.conversationId || undefined,
            message_history: messageHistory,
          };

          if (useWebSocket && wsRef.current?.isConnected()) {
            response = await wsRef.current.sendChatMessage(ChatMode.RAW, input);
          } else {
            response = await apiService.sendRawMessage(input);
          }
        } else {
          // Regular mode
          const input: UserInput = {
            question,
            theme: configStore.theme,
            audience: configStore.audience,
            response_style: configStore.responseStyle,
            context: configStore.context || undefined,
            conversation_id: chatStore.conversationId || undefined,
            message_history: messageHistory,
          };

          if (useWebSocket && wsRef.current?.isConnected()) {
            response = await wsRef.current.sendChatMessage(ChatMode.REGULAR, input);
          } else {
            response = await apiService.sendMessage(input);
          }
        }

        chatStore.addAssistantMessage(response);

        // Set conversation ID if this is the first message
        if (!chatStore.conversationId && response.message_id) {
          chatStore.setConversationId(
            `conv_${response.message_id.substring(0, 8)}`
          );
        }
      } catch (error) {
        console.error('[useChat] Error sending message:', error);
        chatStore.setError(
          error instanceof Error ? error.message : 'Failed to send message'
        );
        chatStore.setLoading(false);
      }
    },
    [chatStore, configStore, useWebSocket]
  );

  /**
   * Rate the last message
   */
  const rateMessage = useCallback(
    async (rating: number, feedback?: string) => {
      if (!chatStore.currentMessageId) {
        throw new Error('No message to rate');
      }

      try {
        await apiService.rateMessage(chatStore.currentMessageId, {
          message_id: chatStore.currentMessageId,
          rating,
          feedback,
        });
      } catch (error) {
        console.error('[useChat] Error rating message:', error);
        throw error;
      }
    },
    [chatStore.currentMessageId]
  );

  /**
   * Clear the current conversation
   */
  const clearConversation = useCallback(() => {
    chatStore.clearMessages();
    chatStore.setConversationId(null);
  }, [chatStore]);

  /**
   * Change chat mode
   */
  const setChatMode = useCallback(
    (mode: ChatMode) => {
      chatStore.setChatMode(mode);
    },
    [chatStore]
  );

  return {
    // State
    messages: chatStore.messages,
    isLoading: chatStore.isLoading,
    error: chatStore.error,
    isConnected: chatStore.isConnected,
    processingStatus: chatStore.processingStatus,
    chatMode: chatStore.chatMode,
    conversationId: chatStore.conversationId,

    // Response metadata
    currentMessageId: chatStore.currentMessageId,
    currentModel: chatStore.currentModel,
    currentProvider: chatStore.currentProvider,
    currentCost: chatStore.currentCost,
    currentResponseTime: chatStore.currentResponseTime,
    currentReasoning: chatStore.currentReasoning,
    currentSystemPrompt: chatStore.currentSystemPrompt,

    // Actions
    sendMessage,
    rateMessage,
    clearConversation,
    setChatMode,
  };
};
