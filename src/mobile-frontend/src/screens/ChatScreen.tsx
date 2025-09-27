/**
 * Main Chat Screen for Mobile App
 * Implements the two-tier chat workflow with React Native
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';

import { getMobileApiService } from '../services/ApiService';
import { ChatMessage } from '../components/ChatMessage';
import { EnhancedOptionsModal } from '../components/EnhancedOptionsModal';
import { THEME_CONFIG, CHAT_CONFIG } from '../constants/Config';

import type {
  ChatMessage as IChatMessage,
  QuickResponse,
  MessageRole,
  ThemeType,
  AudienceType,
} from '../shared/types/api';

interface ExtendedChatMessage extends IChatMessage {
  isQuick?: boolean;
  isEnhanced?: boolean;
  isLoading?: boolean;
}

export default function ChatScreen() {
  const [messages, setMessages] = useState<ExtendedChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showEnhancedModal, setShowEnhancedModal] = useState(false);
  const [currentQuickResponse, setCurrentQuickResponse] = useState<QuickResponse | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState('');

  const flatListRef = useRef<FlatList>(null);
  const apiService = getMobileApiService();

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (messages.length > 0) {
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const question = inputText.trim();
    setCurrentQuestion(question);
    setInputText('');
    setIsLoading(true);

    // Add user message
    const userMessage: ExtendedChatMessage = {
      id: Date.now().toString(),
      role: 'user' as MessageRole,
      content: question,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      // Get quick response
      const quickResponse = await apiService.sendQuickMessage(question);

      const quickMessage: ExtendedChatMessage = {
        id: quickResponse.message_id,
        role: 'assistant' as MessageRole,
        content: quickResponse.content,
        timestamp: new Date().toISOString(),
        isQuick: true,
        metadata: {
          type: 'quick',
          model: quickResponse.model_used,
          provider: quickResponse.provider,
        },
      };

      setMessages(prev => [...prev, quickMessage]);
      setCurrentQuickResponse(quickResponse);

    } catch (error) {
      const errorMessage: ExtendedChatMessage = {
        id: Date.now().toString() + '_error',
        role: 'assistant' as MessageRole,
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
        metadata: {
          type: 'error',
        },
      };

      setMessages(prev => [...prev, errorMessage]);
      console.error('Failed to get quick response:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRequestEnhanced = () => {
    setShowEnhancedModal(true);
  };

  const handleEnhancedSubmit = async (theme: ThemeType, audience: AudienceType) => {
    if (!currentQuestion) return;

    setShowEnhancedModal(false);
    setIsLoading(true);

    try {
      const enhancedResponse = await apiService.sendEnhancedMessage(
        currentQuestion,
        theme,
        audience
      );

      const enhancedMessage: ExtendedChatMessage = {
        id: enhancedResponse.message_id,
        role: 'assistant' as MessageRole,
        content: enhancedResponse.content,
        timestamp: new Date().toISOString(),
        isEnhanced: true,
        metadata: {
          type: 'enhanced',
          model: enhancedResponse.model_used,
          provider: enhancedResponse.provider,
          theme: theme,
          audience: audience,
        },
      };

      // Replace the last assistant message (quick response) with enhanced response
      setMessages(prev => {
        const newMessages = [...prev];
        for (let i = newMessages.length - 1; i >= 0; i--) {
          if (newMessages[i].role === 'assistant') {
            newMessages[i] = enhancedMessage;
            break;
          }
        }
        return newMessages;
      });

    } catch (error) {
      Alert.alert('Error', 'Failed to get enhanced response. Please try again.');
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
    apiService.startNewConversation();
  };

  const renderMessage = ({ item }: { item: ExtendedChatMessage }) => (
    <ChatMessage
      message={item}
      onRequestEnhanced={
        item.isQuick && currentQuickResponse ? handleRequestEnhanced : undefined
      }
    />
  );

  const renderEmptyState = () => (
    <View style={styles.emptyContainer}>
      <Ionicons name="chatbubbles-outline" size={64} color={THEME_CONFIG.colors.textSecondary} />
      <Text style={styles.emptyTitle}>Welcome to PromptYour.AI</Text>
      <Text style={styles.emptySubtitle}>
        Ask any question to get started. You'll receive a quick answer first, then can request an enhanced response tailored to your needs.
      </Text>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        style={styles.keyboardContainer}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 20}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>PromptYour.AI</Text>
          <TouchableOpacity onPress={handleNewChat} style={styles.newChatButton}>
            <Ionicons name="add" size={24} color={THEME_CONFIG.colors.primary} />
          </TouchableOpacity>
        </View>

        {/* Messages List */}
        <FlatList
          ref={flatListRef}
          data={messages}
          keyExtractor={(item) => item.id}
          renderItem={renderMessage}
          style={styles.messagesList}
          contentContainerStyle={messages.length === 0 ? styles.emptyListContainer : styles.messagesContainer}
          ListEmptyComponent={renderEmptyState}
          showsVerticalScrollIndicator={false}
        />

        {/* Loading Indicator */}
        {isLoading && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="small" color={THEME_CONFIG.colors.primary} />
            <Text style={styles.loadingText}>Thinking...</Text>
          </View>
        )}

        {/* Input Area */}
        <View style={styles.inputContainer}>
          <TextInput
            style={styles.textInput}
            value={inputText}
            onChangeText={setInputText}
            placeholder="Ask me anything..."
            placeholderTextColor={THEME_CONFIG.colors.textSecondary}
            multiline
            maxLength={CHAT_CONFIG.maxMessageLength}
            editable={!isLoading}
            onSubmitEditing={handleSendMessage}
          />
          <TouchableOpacity
            style={[
              styles.sendButton,
              {
                backgroundColor: inputText.trim() && !isLoading
                  ? THEME_CONFIG.colors.primary
                  : THEME_CONFIG.colors.border
              }
            ]}
            onPress={handleSendMessage}
            disabled={!inputText.trim() || isLoading}
          >
            <Ionicons
              name="send"
              size={20}
              color={inputText.trim() && !isLoading ? 'white' : THEME_CONFIG.colors.textSecondary}
            />
          </TouchableOpacity>
        </View>

        {/* Enhanced Options Modal */}
        <EnhancedOptionsModal
          visible={showEnhancedModal}
          onClose={() => setShowEnhancedModal(false)}
          onSubmit={handleEnhancedSubmit}
          question={currentQuestion}
        />
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: THEME_CONFIG.colors.background,
  },
  keyboardContainer: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: THEME_CONFIG.spacing.lg,
    paddingVertical: THEME_CONFIG.spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: THEME_CONFIG.colors.border,
    backgroundColor: THEME_CONFIG.colors.background,
  },
  headerTitle: {
    fontSize: THEME_CONFIG.typography.sizes.xl,
    fontWeight: THEME_CONFIG.typography.weights.bold,
    color: THEME_CONFIG.colors.text,
  },
  newChatButton: {
    padding: THEME_CONFIG.spacing.sm,
  },
  messagesList: {
    flex: 1,
  },
  messagesContainer: {
    paddingHorizontal: THEME_CONFIG.spacing.lg,
    paddingVertical: THEME_CONFIG.spacing.md,
  },
  emptyListContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: THEME_CONFIG.spacing.xl,
  },
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: THEME_CONFIG.spacing.xxl,
  },
  emptyTitle: {
    fontSize: THEME_CONFIG.typography.sizes.xl,
    fontWeight: THEME_CONFIG.typography.weights.semibold,
    color: THEME_CONFIG.colors.text,
    marginTop: THEME_CONFIG.spacing.lg,
    textAlign: 'center',
  },
  emptySubtitle: {
    fontSize: THEME_CONFIG.typography.sizes.md,
    color: THEME_CONFIG.colors.textSecondary,
    textAlign: 'center',
    marginTop: THEME_CONFIG.spacing.md,
    lineHeight: 22,
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: THEME_CONFIG.spacing.md,
  },
  loadingText: {
    marginLeft: THEME_CONFIG.spacing.sm,
    color: THEME_CONFIG.colors.textSecondary,
    fontSize: THEME_CONFIG.typography.sizes.sm,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: THEME_CONFIG.spacing.lg,
    paddingVertical: THEME_CONFIG.spacing.md,
    borderTopWidth: 1,
    borderTopColor: THEME_CONFIG.colors.border,
    backgroundColor: THEME_CONFIG.colors.background,
  },
  textInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: THEME_CONFIG.colors.border,
    borderRadius: THEME_CONFIG.borderRadius.lg,
    paddingHorizontal: THEME_CONFIG.spacing.md,
    paddingVertical: THEME_CONFIG.spacing.md,
    fontSize: THEME_CONFIG.typography.sizes.md,
    color: THEME_CONFIG.colors.text,
    backgroundColor: THEME_CONFIG.colors.surface,
    maxHeight: 100,
    marginRight: THEME_CONFIG.spacing.sm,
  },
  sendButton: {
    width: 44,
    height: 44,
    borderRadius: THEME_CONFIG.borderRadius.full,
    justifyContent: 'center',
    alignItems: 'center',
  },
});