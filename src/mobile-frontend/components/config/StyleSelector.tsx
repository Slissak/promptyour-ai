/**
 * StyleSelector Component
 * Dropdown for selecting response style
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { ResponseStyle, ResponseStyleConfig } from '../../types/api';

interface StyleSelectorProps {
  value: ResponseStyle;
  options: ResponseStyleConfig[];
  onChange: (style: ResponseStyle) => void;
}

export const StyleSelector: React.FC<StyleSelectorProps> = ({
  value,
  options,
  onChange,
}) => {
  return (
    <View style={styles.container}>
      <Text style={styles.label}>Response Style</Text>
      <View style={styles.pickerContainer}>
        <Picker
          selectedValue={value}
          onValueChange={onChange}
          style={styles.picker}
          itemStyle={styles.pickerItem}
        >
          {options.map((style) => (
            <Picker.Item
              key={style.id}
              label={style.name}
              value={style.id}
            />
          ))}
        </Picker>
      </View>
      <Text style={styles.description}>
        {options.find((s) => s.id === value)?.description}
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
