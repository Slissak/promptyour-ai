/**
 * MessageList Component
 * Displays the list of chat messages with auto-scroll
 */

import React, { useRef, useEffect } from 'react';
import {
  FlatList,
  View,
  StyleSheet,
  Text,
  ActivityIndicator,
  ListRenderItem,
} from 'react-native';
import { ChatMessage } from '../../types/api';
import { ChatBubble } from './ChatBubble';

interface MessageListProps {
  messages: ChatMessage[];
  isLoading?: boolean;
  processingStatus?: string | null;
  onMessageLongPress?: (message: ChatMessage) => void;
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  isLoading = false,
  processingStatus = null,
  onMessageLongPress,
}) => {
  const flatListRef = useRef<FlatList>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messages.length > 0) {
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages.length]);

  const renderItem: ListRenderItem<ChatMessage> = ({ item }) => (
    <ChatBubble
      message={item}
      onLongPress={() => onMessageLongPress?.(item)}
    />
  );

  const renderEmpty = () => (
    <View style={styles.emptyContainer}>
      <Text style={styles.emptyIcon}>💬</Text>
      <Text style={styles.emptyTitle}>Start a conversation</Text>
      <Text style={styles.emptySubtitle}>
        Ask me anything and I'll help you with enhanced AI responses
      </Text>
    </View>
  );

  const renderFooter = () => {
    if (!isLoading && !processingStatus) return null;

    return (
      <View style={styles.loadingContainer}>
        <View style={styles.loadingBubble}>
          <ActivityIndicator size="small" color="#007AFF" />
          {processingStatus && (
            <Text style={styles.loadingText}>{processingStatus}</Text>
          )}
        </View>
      </View>
    );
  };

  return (
    <FlatList
      ref={flatListRef}
      data={messages}
      renderItem={renderItem}
      keyExtractor={(item, index) => `message-${index}`}
      contentContainerStyle={styles.contentContainer}
      ListEmptyComponent={renderEmpty}
      ListFooterComponent={renderFooter}
      showsVerticalScrollIndicator={true}
      maintainVisibleContentPosition={{
        minIndexForVisible: 0,
      }}
    />
  );
};

const styles = StyleSheet.create({
  contentContainer: {
    flexGrow: 1,
    paddingTop: 12,
    paddingBottom: 12,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emptyIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 22,
    fontWeight: '600',
    color: '#000',
    marginBottom: 8,
    textAlign: 'center',
  },
  emptySubtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 22,
  },
  loadingContainer: {
    alignSelf: 'flex-start',
    marginHorizontal: 12,
    marginVertical: 4,
  },
  loadingBubble: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F0F0F0',
    borderRadius: 16,
    paddingVertical: 10,
    paddingHorizontal: 14,
    gap: 8,
  },
  loadingText: {
    fontSize: 14,
    color: '#666',
    fontStyle: 'italic',
  },
});
