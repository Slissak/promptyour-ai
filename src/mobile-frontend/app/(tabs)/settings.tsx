/**
 * Settings Screen
 * App settings and configuration
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  SafeAreaView,
  Alert,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useUserStore } from '../../store/userStore';
import { useChatStore } from '../../store/chatStore';
import { useConfigStore } from '../../store/configStore';
import { apiService } from '../../services/api';
import { storageService } from '../../services/storage';

export default function SettingsScreen() {
  const userStore = useUserStore();
  const chatStore = useChatStore();
  const configStore = useConfigStore();
  const [apiUrl, setApiUrl] = useState(apiService.getBaseURL());

  const handleClearHistory = () => {
    const confirmAction = () => {
      chatStore.reset();
      if (Platform.OS === 'web') {
        alert('Chat history cleared');
      } else {
        Alert.alert('Success', 'Chat history cleared');
      }
    };

    if (Platform.OS === 'web') {
      if (confirm('Are you sure you want to clear all chat history?')) {
        confirmAction();
      }
    } else {
      Alert.alert(
        'Clear History',
        'Are you sure you want to clear all chat history?',
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Clear', style: 'destructive', onPress: confirmAction },
        ]
      );
    }
  };

  const handleResetConfig = () => {
    const confirmAction = () => {
      configStore.reset();
      if (Platform.OS === 'web') {
        alert('Configuration reset to defaults');
      } else {
        Alert.alert('Success', 'Configuration reset to defaults');
      }
    };

    if (Platform.OS === 'web') {
      if (confirm('Reset all configuration to defaults?')) {
        confirmAction();
      }
    } else {
      Alert.alert(
        'Reset Configuration',
        'Reset all configuration to defaults?',
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Reset', style: 'destructive', onPress: confirmAction },
        ]
      );
    }
  };

  const handleUpdateApiUrl = async () => {
    try {
      apiService.setBaseURL(apiUrl);
      await storageService.setApiBaseUrl(apiUrl);
      if (Platform.OS === 'web') {
        alert('API URL updated successfully');
      } else {
        Alert.alert('Success', 'API URL updated successfully');
      }
    } catch (error) {
      if (Platform.OS === 'web') {
        alert('Failed to update API URL');
      } else {
        Alert.alert('Error', 'Failed to update API URL');
      }
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
        <Text style={styles.sectionTitle}>Account</Text>
        <View style={styles.section}>
          <View style={styles.settingRow}>
            <Text style={styles.settingLabel}>User ID</Text>
            <Text style={styles.settingValue}>{userStore.userId}</Text>
          </View>
        </View>

        <Text style={styles.sectionTitle}>API Configuration</Text>
        <View style={styles.section}>
          <View style={styles.settingRow}>
            <Text style={styles.settingLabel}>Backend URL</Text>
          </View>
          <TextInput
            style={styles.textInput}
            value={apiUrl}
            onChangeText={setApiUrl}
            placeholder="http://localhost:8001"
            placeholderTextColor="#999"
            autoCapitalize="none"
            autoCorrect={false}
          />
          <TouchableOpacity
            style={styles.button}
            onPress={handleUpdateApiUrl}
          >
            <Text style={styles.buttonText}>Update URL</Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.sectionTitle}>Data Management</Text>
        <View style={styles.section}>
          <TouchableOpacity
            style={styles.settingButton}
            onPress={handleClearHistory}
          >
            <Ionicons name="trash-outline" size={20} color="#FF3B30" />
            <Text style={[styles.settingButtonText, { color: '#FF3B30' }]}>
              Clear Chat History
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.settingButton}
            onPress={handleResetConfig}
          >
            <Ionicons name="refresh-outline" size={20} color="#FF9500" />
            <Text style={[styles.settingButtonText, { color: '#FF9500' }]}>
              Reset Configuration
            </Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.sectionTitle}>About</Text>
        <View style={styles.section}>
          <View style={styles.settingRow}>
            <Text style={styles.settingLabel}>Version</Text>
            <Text style={styles.settingValue}>1.0.0</Text>
          </View>
          <View style={styles.settingRow}>
            <Text style={styles.settingLabel}>Platform</Text>
            <Text style={styles.settingValue}>
              {Platform.OS === 'web' ? 'Web' : Platform.OS === 'ios' ? 'iOS' : 'Android'}
            </Text>
          </View>
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>
            🤖 PromptYour.AI
          </Text>
          <Text style={styles.footerSubtext}>
            Enhanced AI responses through intelligent model routing
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  container: {
    flex: 1,
  },
  content: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    textTransform: 'uppercase',
    marginTop: 24,
    marginBottom: 8,
    marginLeft: 4,
  },
  section: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  settingLabel: {
    fontSize: 16,
    color: '#000',
  },
  settingValue: {
    fontSize: 14,
    color: '#666',
  },
  textInput: {
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E0E0E0',
    padding: 12,
    fontSize: 14,
    color: '#000',
    marginTop: 8,
    marginBottom: 12,
  },
  button: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: 'center',
  },
  buttonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '600',
  },
  settingButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    gap: 12,
  },
  settingButtonText: {
    fontSize: 16,
    fontWeight: '500',
  },
  footer: {
    alignItems: 'center',
    marginTop: 32,
    marginBottom: 16,
  },
  footerText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#000',
    marginBottom: 4,
  },
  footerSubtext: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
});
