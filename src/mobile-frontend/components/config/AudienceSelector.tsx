/**
 * AudienceSelector Component
 * Dropdown for selecting target audience
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { AudienceType, AudienceConfig } from '../../types/api';

interface AudienceSelectorProps {
  value: AudienceType;
  options: AudienceConfig[];
  onChange: (audience: AudienceType) => void;
}

export const AudienceSelector: React.FC<AudienceSelectorProps> = ({
  value,
  options,
  onChange,
}) => {
  return (
    <View style={styles.container}>
      <Text style={styles.label}>Audience</Text>
      <View style={styles.pickerContainer}>
        <Picker
          selectedValue={value}
          onValueChange={onChange}
          style={styles.picker}
          itemStyle={styles.pickerItem}
        >
          {options.map((audience) => (
            <Picker.Item
              key={audience.id}
              label={audience.name}
              value={audience.id}
            />
          ))}
        </Picker>
      </View>
      <Text style={styles.description}>
        {options.find((a) => a.id === value)?.description}
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
  pickerContainer: {
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E0E0E0',
    overflow: 'hidden',
  },
  picker: {
    height: 50,
  },
  pickerItem: {
    fontSize: 16,
  },
  description: {
    fontSize: 12,
    color: '#666',
    marginTop: 6,
  },
});
