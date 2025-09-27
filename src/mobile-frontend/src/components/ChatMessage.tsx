/**
 * Chat Message Component
 * Displays individual messages with support for quick and enhanced responses
 */

import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Animated,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { THEME_CONFIG } from '../constants/Config';

import type { ChatMessage as IChatMessage } from '../shared/types/api';

interface ExtendedChatMessage extends IChatMessage {
  isQuick?: boolean;
  isEnhanced?: boolean;
}

interface ChatMessageProps {
  message: ExtendedChatMessage;
  onRequestEnhanced?: () => void;
}

export function ChatMessage({ message, onRequestEnhanced }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const isQuick = message.metadata?.type === 'quick';
  const isEnhanced = message.metadata?.type === 'enhanced';
  const isError = message.metadata?.type === 'error';

  const getBubbleStyle = () => {
    if (isUser) {
      return {
        backgroundColor: THEME_CONFIG.colors.primary,
        alignSelf: 'flex-end' as const,
        marginLeft: 48,
      };
    } else if (isError) {
      return {
        backgroundColor: '#FEE2E2',
        borderColor: '#FCA5A5',
        alignSelf: 'flex-start' as const,
        marginRight: 48,
      };
    } else if (isQuick) {
      return {
        backgroundColor: THEME_CONFIG.colors.quick,
        borderColor: THEME_CONFIG.colors.quickBorder,
        borderWidth: 1,
        alignSelf: 'flex-start' as const,
        marginRight: 48,
      };
    } else {
      return {
        backgroundColor: THEME_CONFIG.colors.surface,
        alignSelf: 'flex-start' as const,
        marginRight: 48,
      };
    }
  };

  const getTextColor = () => {
    if (isUser) return 'white';
    if (isError) return '#B91C1C';
    return THEME_CONFIG.colors.text;
  };

  return (
    <View style={styles.messageContainer}>
      {/* Message Badge */}
      {(isQuick || isEnhanced) && (
        <View style={styles.badgeContainer}>
          <View style={[
            styles.badge,
            {
              backgroundColor: isQuick ? THEME_CONFIG.colors.quickBorder : THEME_CONFIG.colors.primary
            }
          ]}>
            <Text style={styles.badgeText}>
              {isQuick ? '⚡ Quick' : '✨ Enhanced'}
            </Text>
          </View>
          {message.metadata?.theme && message.metadata?.audience && (
            <Text style={styles.metadataText}>
              {message.metadata.theme.replace('_', ' ')} • {message.metadata.audience.replace('_', ' ')}
            </Text>
          )}
        </View>
      )}

      {/* Message Bubble */}
      <View style={[styles.messageBubble, getBubbleStyle()]}>
        <Text style={[styles.messageText, { color: getTextColor() }]}>
          {message.content}
        </Text>

        {/* Model info */}
        {!isUser && message.metadata?.model && (
          <Text style={[styles.modelInfo, { color: getTextColor(), opacity: 0.7 }]}>
            {message.metadata.model} via {message.metadata.provider}
          </Text>
        )}
      </View>

      {/* Quick Response Action */}
      {isQuick && onRequestEnhanced && (
        <View style={styles.actionContainer}>
          <TouchableOpacity style={styles.enhancedButton} onPress={onRequestEnhanced}>
            <Ionicons name="sparkles" size={16} color={THEME_CONFIG.colors.primary} />
            <Text style={styles.enhancedButtonText}>Get Enhanced Response</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Timestamp */}
      <Text style={[
        styles.timestamp,
        { textAlign: isUser ? 'right' : 'left' }
      ]}>
        {message.timestamp ? new Date(message.timestamp).toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit'
        }) : ''}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  messageContainer: {
    marginBottom: THEME_CONFIG.spacing.lg,
  },
  badgeContainer: {
    marginBottom: THEME_CONFIG.spacing.xs,
    alignItems: 'flex-start',
  },
  badge: {
    paddingHorizontal: THEME_CONFIG.spacing.sm,
    paddingVertical: THEME_CONFIG.spacing.xs,
    borderRadius: THEME_CONFIG.borderRadius.full,
    marginBottom: THEME_CONFIG.spacing.xs / 2,
  },
  badgeText: {
    fontSize: THEME_CONFIG.typography.sizes.xs,
    color: 'white',
    fontWeight: THEME_CONFIG.typography.weights.medium,
  },
  metadataText: {
    fontSize: THEME_CONFIG.typography.sizes.xs,
    color: THEME_CONFIG.colors.textSecondary,
  },
  messageBubble: {
    paddingHorizontal: THEME_CONFIG.spacing.md,
    paddingVertical: THEME_CONFIG.spacing.md,
    borderRadius: THEME_CONFIG.borderRadius.lg,
    maxWidth: '85%',
  },
  messageText: {
    fontSize: THEME_CONFIG.typography.sizes.md,
    lineHeight: 20,
  },
  modelInfo: {
    fontSize: THEME_CONFIG.typography.sizes.xs,
    marginTop: THEME_CONFIG.spacing.xs,
  },
  actionContainer: {
    alignItems: 'center',
    marginTop: THEME_CONFIG.spacing.sm,
  },
  enhancedButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: THEME_CONFIG.spacing.md,
    paddingVertical: THEME_CONFIG.spacing.sm,
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: THEME_CONFIG.colors.primary,
    borderRadius: THEME_CONFIG.borderRadius.full,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  enhancedButtonText: {
    marginLeft: THEME_CONFIG.spacing.xs,
    fontSize: THEME_CONFIG.typography.sizes.sm,
    color: THEME_CONFIG.colors.primary,
    fontWeight: THEME_CONFIG.typography.weights.medium,
  },
  timestamp: {
    fontSize: THEME_CONFIG.typography.sizes.xs,
    color: THEME_CONFIG.colors.textSecondary,
    marginTop: THEME_CONFIG.spacing.xs,
  },
});