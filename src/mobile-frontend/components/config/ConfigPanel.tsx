/**
 * ConfigPanel Component
 * Container for all configuration options
 */

import React from 'react';
import {
  View,
  Text,
  TextInput,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { ChatMode, ThemeType, AudienceType, ResponseStyle } from '../../types/api';
import { ModeSwitch } from './ModeSwitch';
import { ThemeSelector } from './ThemeSelector';
import { AudienceSelector } from './AudienceSelector';
import { StyleSelector } from './StyleSelector';
import { useConfigStore } from '../../store/configStore';

interface ConfigPanelProps {
  chatMode: ChatMode;
  onChatModeChange: (mode: ChatMode) => void;
  onClose?: () => void;
  isEmbedded?: boolean; // If true, hide header and mode switch (for side panel)
}

export const ConfigPanel: React.FC<ConfigPanelProps> = ({
  chatMode,
  onChatModeChange,
  onClose,
  isEmbedded = false,
}) => {
  const configStore = useConfigStore();

  const showFullConfig = chatMode === ChatMode.REGULAR;

  return (
    <View style={[styles.container, isEmbedded && styles.containerEmbedded]}>
      {/* Header - hide in embedded mode */}
      {!isEmbedded && (
        <View style={styles.header}>
          <Text style={styles.title}>Configuration</Text>
          {onClose && (
            <TouchableOpacity onPress={onClose} style={styles.closeButton}>
              <Ionicons name="close" size={24} color="#333" />
            </TouchableOpacity>
          )}
        </View>
      )}

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={[
          styles.content,
          isEmbedded && styles.contentEmbedded,
        ]}
        showsVerticalScrollIndicator={true}
      >
        {/* Chat Mode Selector - hide in embedded mode */}
        {!isEmbedded && (
          <ModeSwitch mode={chatMode} onChange={onChatModeChange} />
        )}

        {/* Show full config in Regular mode or embedded mode */}
        {(showFullConfig || isEmbedded) && (
          <>
            {/* Theme Selector */}
            {configStore.themes.length > 0 && (
              <ThemeSelector
                value={configStore.theme}
                options={configStore.themes}
                onChange={configStore.setTheme}
              />
            )}

            {/* Audience Selector */}
            {configStore.audiences.length > 0 && (
              <AudienceSelector
                value={configStore.audience}
                options={configStore.audiences}
                onChange={configStore.setAudience}
              />
            )}

            {/* Response Style Selector */}
            {configStore.responseStyles.length > 0 && (
              <StyleSelector
                value={configStore.responseStyle}
                options={configStore.responseStyles}
                onChange={configStore.setResponseStyle}
              />
            )}

            {/* Context Input */}
            <View style={styles.inputContainer}>
              <Text style={styles.label}>Additional Context (Optional)</Text>
              <TextInput
                style={styles.textInput}
                value={configStore.context}
                onChangeText={configStore.setContext}
                placeholder="Add any additional context or instructions..."
                placeholderTextColor="#999"
                multiline
                numberOfLines={3}
                maxLength={500}
              />
              <Text style={styles.charCount}>
                {configStore.context.length}/500
              </Text>
            </View>
          </>
        )}

        {/* Info for Quick and Raw modes - don't show in embedded mode */}
        {!showFullConfig && !isEmbedded && (
          <View style={styles.infoBox}>
            <Ionicons name="information-circle" size={24} color="#007AFF" />
            <Text style={styles.infoText}>
              {chatMode === ChatMode.QUICK
                ? 'Quick mode uses fast responses without customization. Perfect for simple questions.'
                : 'Raw mode sends your question directly to the model without any prompt engineering. Use this to compare against enhanced responses.'}
            </Text>
          </View>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFF',
  },
  containerEmbedded: {
    backgroundColor: 'transparent',
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
  title: {
    fontSize: 20,
    fontWeight: '600',
    color: '#000',
  },
  closeButton: {
    padding: 4,
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 16,
  },
  contentEmbedded: {
    paddingTop: 0,
  },
  inputContainer: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  textInput: {
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E0E0E0',
    padding: 12,
    fontSize: 14,
    color: '#000',
    minHeight: 80,
    textAlignVertical: 'top',
  },
  charCount: {
    fontSize: 12,
    color: '#999',
    textAlign: 'right',
    marginTop: 4,
  },
  infoBox: {
    flexDirection: 'row',
    backgroundColor: '#F0F8FF',
    borderRadius: 8,
    padding: 12,
    gap: 12,
    marginTop: 8,
  },
  infoText: {
    flex: 1,
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
});
