/**
 * ChatBubble Component
 * Displays individual chat messages in bubble format
 */

import React from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { MessageRole, ChatMessage } from '../../types/api';

interface ChatBubbleProps {
  message: ChatMessage;
  onLongPress?: () => void;
}

export const ChatBubble: React.FC<ChatBubbleProps> = ({
  message,
  onLongPress,
}) => {
  const isUser = message.role === MessageRole.USER;

  return (
    <Pressable
      onLongPress={onLongPress}
      style={[styles.container, isUser ? styles.userContainer : styles.assistantContainer]}
    >
      <View style={[styles.bubble, isUser ? styles.userBubble : styles.assistantBubble]}>
        <Text style={[styles.text, isUser ? styles.userText : styles.assistantText]}>
          {message.content}
        </Text>

        {message.timestamp && (
          <Text style={styles.timestamp}>
            {new Date(message.timestamp).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </Text>
        )}

        {message.model && !isUser && (
          <Text style={styles.modelInfo}>
            {message.model} • {message.provider}
          </Text>
        )}
      </View>
    </Pressable>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 4,
    marginHorizontal: 12,
    maxWidth: '80%',
  },
  userContainer: {
    alignSelf: 'flex-end',
  },
  assistantContainer: {
    alignSelf: 'flex-start',
  },
  bubble: {
    borderRadius: 16,
    paddingVertical: 10,
    paddingHorizontal: 14,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  userBubble: {
    backgroundColor: '#007AFF',
    borderBottomRightRadius: 4,
  },
  assistantBubble: {
    backgroundColor: '#F0F0F0',
    borderBottomLeftRadius: 4,
  },
  text: {
    fontSize: 16,
    lineHeight: 22,
  },
  userText: {
    color: '#FFFFFF',
  },
  assistantText: {
    color: '#000000',
  },
  timestamp: {
    fontSize: 11,
    marginTop: 4,
    opacity: 0.6,
  },
  modelInfo: {
    fontSize: 10,
    marginTop: 4,
    opacity: 0.5,
    fontStyle: 'italic',
  },
});
