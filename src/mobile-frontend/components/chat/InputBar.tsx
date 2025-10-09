/**
 * InputBar Component
 * Message input field with send button
 */

import React, { useState } from 'react';
import {
  View,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Platform,
  KeyboardAvoidingView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface InputBarProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export const InputBar: React.FC<InputBarProps> = ({
  onSend,
  disabled = false,
  placeholder = 'Type your message...',
}) => {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
    >
      <View style={styles.container}>
        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            value={message}
            onChangeText={setMessage}
            placeholder={placeholder}
            placeholderTextColor="#999"
            multiline
            maxLength={2000}
            editable={!disabled}
            onSubmitEditing={handleSend}
            blurOnSubmit={false}
          />

          <TouchableOpacity
            style={[
              styles.sendButton,
              (!message.trim() || disabled) && styles.sendButtonDisabled,
            ]}
            onPress={handleSend}
            disabled={!message.trim() || disabled}
          >
            <Ionicons
              name="send"
              size={20}
              color={!message.trim() || disabled ? '#CCC' : '#FFF'}
            />
          </TouchableOpacity>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#FFF',
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
    paddingHorizontal: 12,
    paddingVertical: 8,
    ...Platform.select({
      web: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: -2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
      },
    }),
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 8,
  },
  input: {
    flex: 1,
    minHeight: 40,
    maxHeight: 120,
    backgroundColor: '#F5F5F5',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    fontSize: 16,
    color: '#000',
    ...Platform.select({
      web: {
        outlineStyle: 'none',
      },
    }),
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonDisabled: {
    backgroundColor: '#F0F0F0',
  },
});
