/**
 * Enhanced Options Modal
 * Modal for selecting theme and audience for enhanced responses
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  Modal,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  Pressable,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { THEME_CONFIG } from '../constants/Config';

import type { ThemeType, AudienceType } from '../shared/types/api';
import { THEME_INFO, AUDIENCE_INFO } from '../shared/types/constants';

interface EnhancedOptionsModalProps {
  visible: boolean;
  onClose: () => void;
  onSubmit: (theme: ThemeType, audience: AudienceType) => void;
  question: string;
}

export function EnhancedOptionsModal({
  visible,
  onClose,
  onSubmit,
  question
}: EnhancedOptionsModalProps) {
  const [selectedTheme, setSelectedTheme] = useState<ThemeType>('general_questions' as ThemeType);
  const [selectedAudience, setSelectedAudience] = useState<AudienceType>('adults' as AudienceType);

  const handleSubmit = () => {
    onSubmit(selectedTheme, selectedAudience);
  };

  const themes = Object.values(THEME_INFO);
  const audiences = Object.values(AUDIENCE_INFO);

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose}
    >
      <View style={styles.modalContainer}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>✨ Enhanced Response</Text>
          <TouchableOpacity onPress={onClose} style={styles.closeButton}>
            <Ionicons name="close" size={24} color={THEME_CONFIG.colors.text} />
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          {/* Question Preview */}
          <View style={styles.questionContainer}>
            <Text style={styles.questionLabel}>Your Question:</Text>
            <Text style={styles.questionText}>{question}</Text>
          </View>

          {/* Theme Selection */}
          <View style={styles.sectionContainer}>
            <Text style={styles.sectionTitle}>Choose a Theme</Text>
            <View style={styles.optionsGrid}>
              {themes.map((theme) => (
                <TouchableOpacity
                  key={theme.id}
                  style={[
                    styles.optionCard,
                    selectedTheme === theme.id && styles.selectedCard
                  ]}
                  onPress={() => setSelectedTheme(theme.id)}
                >
                  <Text style={styles.optionIcon}>{theme.icon}</Text>
                  <Text style={[
                    styles.optionTitle,
                    selectedTheme === theme.id && styles.selectedText
                  ]}>
                    {theme.name}
                  </Text>
                  <Text style={[
                    styles.optionDescription,
                    selectedTheme === theme.id && styles.selectedDescription
                  ]}>
                    {theme.description}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {/* Audience Selection */}
          <View style={styles.sectionContainer}>
            <Text style={styles.sectionTitle}>Choose Your Audience</Text>
            <View style={styles.optionsGrid}>
              {audiences.map((audience) => (
                <TouchableOpacity
                  key={audience.id}
                  style={[
                    styles.optionCard,
                    selectedAudience === audience.id && styles.selectedCard
                  ]}
                  onPress={() => setSelectedAudience(audience.id)}
                >
                  <Text style={styles.optionIcon}>{audience.icon}</Text>
                  <Text style={[
                    styles.optionTitle,
                    selectedAudience === audience.id && styles.selectedText
                  ]}>
                    {audience.name}
                  </Text>
                  <Text style={[
                    styles.optionDescription,
                    selectedAudience === audience.id && styles.selectedDescription
                  ]}>
                    {audience.ageRange}
                  </Text>
                  <Text style={[
                    styles.optionSubDescription,
                    selectedAudience === audience.id && styles.selectedDescription
                  ]}>
                    {audience.description}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </ScrollView>

        {/* Footer */}
        <View style={styles.footer}>
          <TouchableOpacity style={styles.cancelButton} onPress={onClose}>
            <Text style={styles.cancelButtonText}>Cancel</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.submitButton} onPress={handleSubmit}>
            <Text style={styles.submitButtonText}>Get Enhanced Answer</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  modalContainer: {
    flex: 1,
    backgroundColor: THEME_CONFIG.colors.background,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: THEME_CONFIG.spacing.lg,
    paddingVertical: THEME_CONFIG.spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: THEME_CONFIG.colors.border,
  },
  headerTitle: {
    fontSize: THEME_CONFIG.typography.sizes.lg,
    fontWeight: THEME_CONFIG.typography.weights.semibold,
    color: THEME_CONFIG.colors.text,
  },
  closeButton: {
    padding: THEME_CONFIG.spacing.sm,
  },
  content: {
    flex: 1,
    paddingHorizontal: THEME_CONFIG.spacing.lg,
  },
  questionContainer: {
    backgroundColor: THEME_CONFIG.colors.surface,
    padding: THEME_CONFIG.spacing.md,
    borderRadius: THEME_CONFIG.borderRadius.md,
    borderLeftWidth: 4,
    borderLeftColor: THEME_CONFIG.colors.primary,
    marginVertical: THEME_CONFIG.spacing.lg,
  },
  questionLabel: {
    fontSize: THEME_CONFIG.typography.sizes.sm,
    fontWeight: THEME_CONFIG.typography.weights.medium,
    color: THEME_CONFIG.colors.textSecondary,
    marginBottom: THEME_CONFIG.spacing.xs,
  },
  questionText: {
    fontSize: THEME_CONFIG.typography.sizes.md,
    color: THEME_CONFIG.colors.text,
    lineHeight: 22,
  },
  sectionContainer: {
    marginBottom: THEME_CONFIG.spacing.xl,
  },
  sectionTitle: {
    fontSize: THEME_CONFIG.typography.sizes.lg,
    fontWeight: THEME_CONFIG.typography.weights.semibold,
    color: THEME_CONFIG.colors.text,
    marginBottom: THEME_CONFIG.spacing.md,
  },
  optionsGrid: {
    gap: THEME_CONFIG.spacing.md,
  },
  optionCard: {
    padding: THEME_CONFIG.spacing.md,
    borderRadius: THEME_CONFIG.borderRadius.md,
    borderWidth: 1,
    borderColor: THEME_CONFIG.colors.border,
    backgroundColor: THEME_CONFIG.colors.background,
  },
  selectedCard: {
    borderColor: THEME_CONFIG.colors.primary,
    backgroundColor: THEME_CONFIG.colors.enhanced,
    shadowColor: THEME_CONFIG.colors.primary,
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  optionIcon: {
    fontSize: 24,
    marginBottom: THEME_CONFIG.spacing.xs,
  },
  optionTitle: {
    fontSize: THEME_CONFIG.typography.sizes.md,
    fontWeight: THEME_CONFIG.typography.weights.semibold,
    color: THEME_CONFIG.colors.text,
    marginBottom: THEME_CONFIG.spacing.xs / 2,
  },
  optionDescription: {
    fontSize: THEME_CONFIG.typography.sizes.sm,
    color: THEME_CONFIG.colors.textSecondary,
    lineHeight: 18,
  },
  optionSubDescription: {
    fontSize: THEME_CONFIG.typography.sizes.xs,
    color: THEME_CONFIG.colors.textSecondary,
    lineHeight: 16,
    marginTop: THEME_CONFIG.spacing.xs / 2,
  },
  selectedText: {
    color: THEME_CONFIG.colors.primary,
  },
  selectedDescription: {
    color: THEME_CONFIG.colors.text,
  },
  footer: {
    flexDirection: 'row',
    paddingHorizontal: THEME_CONFIG.spacing.lg,
    paddingVertical: THEME_CONFIG.spacing.md,
    borderTopWidth: 1,
    borderTopColor: THEME_CONFIG.colors.border,
    gap: THEME_CONFIG.spacing.md,
  },
  cancelButton: {
    flex: 1,
    paddingVertical: THEME_CONFIG.spacing.md,
    borderRadius: THEME_CONFIG.borderRadius.md,
    backgroundColor: THEME_CONFIG.colors.surface,
    alignItems: 'center',
  },
  cancelButtonText: {
    fontSize: THEME_CONFIG.typography.sizes.md,
    fontWeight: THEME_CONFIG.typography.weights.medium,
    color: THEME_CONFIG.colors.text,
  },
  submitButton: {
    flex: 2,
    paddingVertical: THEME_CONFIG.spacing.md,
    borderRadius: THEME_CONFIG.borderRadius.md,
    backgroundColor: THEME_CONFIG.colors.primary,
    alignItems: 'center',
  },
  submitButtonText: {
    fontSize: THEME_CONFIG.typography.sizes.md,
    fontWeight: THEME_CONFIG.typography.weights.medium,
    color: 'white',
  },
});