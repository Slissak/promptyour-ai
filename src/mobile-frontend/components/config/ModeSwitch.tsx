/**
 * ModeSwitch Component
 * Toggle between Regular, Quick, and Raw chat modes
 */

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { ChatMode } from '../../types/api';

interface ModeSwitchProps {
  mode: ChatMode;
  onChange: (mode: ChatMode) => void;
}

const MODES = [
  {
    value: ChatMode.REGULAR,
    label: 'Regular',
    description: 'Full customization with theme & audience',
  },
  {
    value: ChatMode.QUICK,
    label: 'Quick',
    description: 'Fast responses without customization',
  },
  {
    value: ChatMode.RAW,
    label: 'Raw',
    description: 'No prompt engineering (comparison)',
  },
];

export const ModeSwitch: React.FC<ModeSwitchProps> = ({ mode, onChange }) => {
  return (
    <View style={styles.container}>
      <Text style={styles.label}>Chat Mode</Text>
      <View style={styles.modeContainer}>
        {MODES.map((modeOption) => (
          <TouchableOpacity
            key={modeOption.value}
            style={[
              styles.modeButton,
              mode === modeOption.value && styles.modeButtonActive,
            ]}
            onPress={() => onChange(modeOption.value)}
          >
            <Text
              style={[
                styles.modeLabel,
                mode === modeOption.value && styles.modeLabelActive,
              ]}
            >
              {modeOption.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
      <Text style={styles.description}>
        {MODES.find((m) => m.value === mode)?.description}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  modeContainer: {
    flexDirection: 'row',
    backgroundColor: '#F0F0F0',
    borderRadius: 8,
    padding: 2,
  },
  modeButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 6,
    alignItems: 'center',
  },
  modeButtonActive: {
    backgroundColor: '#007AFF',
  },
  modeLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#666',
  },
  modeLabelActive: {
    color: '#FFF',
  },
  description: {
    fontSize: 12,
    color: '#666',
    marginTop: 6,
    textAlign: 'center',
  },
});
