/**
 * Chat Screen
 * Main chat interface with configuration panel
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  SafeAreaView,
  Platform,
  Alert,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { MessageList } from '../../components/chat/MessageList';
import { InputBar } from '../../components/chat/InputBar';
import { ConfigPanel } from '../../components/config/ConfigPanel';
import { useChat } from '../../hooks/useChat';
import { useConfigStore } from '../../store/configStore';
import { useUserStore } from '../../store/userStore';
import { apiService } from '../../services/api';
import { ChatMessage } from '../../types/api';

export default function ChatScreen() {
  const [configVisible, setConfigVisible] = useState(false);
  const [enhancedModeEnabled, setEnhancedModeEnabled] = useState(false);
  const userStore = useUserStore();
  const configStore = useConfigStore();
  const chat = useChat();

  // Initialize user and load config on mount
  useEffect(() => {
    const initialize = async () => {
      try {
        // Initialize user
        if (!userStore.isInitialized) {
          await userStore.initializeUser();
        }

        // Load saved config from storage
        await configStore.loadFromStorage();

        // Load themes, audiences, and styles from API
        const [themesResponse, audiencesResponse, stylesResponse] =
          await Promise.all([
            apiService.getThemes(),
            apiService.getAudiences(),
            apiService.getResponseStyles(),
          ]);

        configStore.setThemes(themesResponse.themes || []);
        configStore.setAudiences(audiencesResponse.audiences || []);
        configStore.setResponseStyles(stylesResponse.response_styles || []);
      } catch (error) {
        console.error('[ChatScreen] Initialization error:', error);
        // Use default values if API fails
      }
    };

    initialize();
  }, []);

  const handleSendMessage = async (message: string) => {
    try {
      await chat.sendMessage(message);
    } catch (error) {
      console.error('[ChatScreen] Send message error:', error);
      if (Platform.OS === 'web') {
        alert('Failed to send message. Please check your connection.');
      } else {
        Alert.alert('Error', 'Failed to send message. Please try again.');
      }
    }
  };

  const handleMessageLongPress = (message: ChatMessage) => {
    // Show options menu (copy, share, etc.)
    if (Platform.OS === 'web') {
      // Web: Copy to clipboard
      navigator.clipboard.writeText(message.content);
      alert('Message copied to clipboard');
    } else {
      // Mobile: Show action sheet
      Alert.alert(
        'Message Options',
        'What would you like to do?',
        [
          {
            text: 'Copy',
            onPress: () => {
              // TODO: Copy to clipboard on mobile
              console.log('Copy message:', message.content);
            },
          },
          {
            text: 'Cancel',
            style: 'cancel',
          },
        ],
        { cancelable: true }
      );
    }
  };

  // Quick mode uses split layout, other modes use modal
  const isQuickMode = chat.chatMode === 'quick';

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        {/* Header with config button and mode toggle */}
        <View style={styles.header}>
          <View style={styles.headerLeft}>
            <TouchableOpacity
              style={styles.configButton}
              onPress={() => setConfigVisible(true)}
            >
              <Ionicons name="settings-outline" size={24} color="#007AFF" />
            </TouchableOpacity>

            {/* Quick mode: Show enhanced mode toggle */}
            {isQuickMode && (
              <TouchableOpacity
                style={[
                  styles.enhancedButton,
                  enhancedModeEnabled && styles.enhancedButtonActive,
                ]}
                onPress={() => {
                  setEnhancedModeEnabled(!enhancedModeEnabled);
                  if (!enhancedModeEnabled) {
                    // Switch to regular mode when enabling enhanced
                    chat.setChatMode('regular');
                  } else {
                    // Switch back to quick mode when disabling
                    chat.setChatMode('quick');
                  }
                }}
              >
                <Ionicons
                  name={enhancedModeEnabled ? 'options' : 'options-outline'}
                  size={20}
                  color={enhancedModeEnabled ? '#FFF' : '#007AFF'}
                />
                <Text
                  style={[
                    styles.enhancedButtonText,
                    enhancedModeEnabled && styles.enhancedButtonTextActive,
                  ]}
                >
                  Enhanced
                </Text>
              </TouchableOpacity>
            )}
          </View>

          {/* Connection indicator */}
          {chat.isConnected && (
            <View style={styles.connectionIndicator}>
              <View style={styles.connectedDot} />
            </View>
          )}
        </View>

        {/* Main content area */}
        <View style={styles.mainContent}>
          {/* Chat area (left side in Quick mode with enhanced panel) */}
          <View
            style={[
              styles.chatArea,
              isQuickMode && enhancedModeEnabled && styles.chatAreaSplit,
            ]}
          >
            {/* Message List */}
            <MessageList
              messages={chat.messages}
              isLoading={chat.isLoading}
              processingStatus={chat.processingStatus}
              onMessageLongPress={handleMessageLongPress}
            />

            {/* Error message */}
            {chat.error && (
              <View style={styles.errorContainer}>
                <Ionicons name="alert-circle" size={20} color="#FF3B30" />
                <Text style={styles.errorText}>{chat.error}</Text>
              </View>
            )}

            {/* Input Bar */}
            <InputBar
              onSend={handleSendMessage}
              disabled={chat.isLoading}
              placeholder={
                enhancedModeEnabled
                  ? 'Configure on the right, then ask...'
                  : chat.chatMode === 'quick'
                  ? 'Ask a quick question...'
                  : chat.chatMode === 'raw'
                  ? 'Ask without prompt engineering...'
                  : 'Type your message...'
              }
            />
          </View>

          {/* Enhanced config panel (right side in Quick mode) */}
          {isQuickMode && enhancedModeEnabled && (
            <View style={styles.enhancedPanel}>
              <ScrollView style={styles.enhancedPanelScroll}>
                <Text style={styles.enhancedPanelTitle}>
                  Enhanced Configuration
                </Text>
                <Text style={styles.enhancedPanelSubtitle}>
                  Customize your response
                </Text>

                <ConfigPanel
                  chatMode={chat.chatMode}
                  onChatModeChange={(mode) => {
                    // Don't allow switching modes from side panel
                  }}
                  onClose={() => {}}
                  isEmbedded={true}
                />
              </ScrollView>
            </View>
          )}
        </View>

        {/* Config Panel Modal (for non-Quick modes or settings) */}
        <Modal
          visible={configVisible}
          animationType="slide"
          presentationStyle={Platform.OS === 'ios' ? 'pageSheet' : 'fullScreen'}
          onRequestClose={() => setConfigVisible(false)}
        >
          <SafeAreaView style={styles.modalContainer}>
            <ConfigPanel
              chatMode={chat.chatMode}
              onChatModeChange={chat.setChatMode}
              onClose={() => setConfigVisible(false)}
            />
          </SafeAreaView>
        </Modal>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#FFF',
  },
  container: {
    flex: 1,
    backgroundColor: '#FFF',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  configButton: {
    padding: 4,
  },
  enhancedButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#007AFF',
    gap: 6,
  },
  enhancedButtonActive: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF',
  },
  enhancedButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#007AFF',
  },
  enhancedButtonTextActive: {
    color: '#FFF',
  },
  connectionIndicator: {
    padding: 4,
  },
  connectedDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#34C759',
  },
  mainContent: {
    flex: 1,
    flexDirection: 'row',
  },
  chatArea: {
    flex: 1,
    backgroundColor: '#FFF',
  },
  chatAreaSplit: {
    flex: 0.65, // 65% width when panel is shown
    borderRightWidth: 1,
    borderRightColor: '#E0E0E0',
  },
  enhancedPanel: {
    flex: 0.35, // 35% width
    backgroundColor: '#F8F9FA',
    borderLeftWidth: 1,
    borderLeftColor: '#E0E0E0',
  },
  enhancedPanelScroll: {
    flex: 1,
  },
  enhancedPanelTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1A1A1A',
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 4,
  },
  enhancedPanelSubtitle: {
    fontSize: 14,
    color: '#666',
    paddingHorizontal: 16,
    paddingBottom: 16,
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFEBEE',
    paddingHorizontal: 16,
    paddingVertical: 12,
    gap: 8,
    borderTopWidth: 1,
    borderTopColor: '#FFCDD2',
  },
  errorText: {
    flex: 1,
    fontSize: 14,
    color: '#D32F2F',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#FFF',
  },
});
