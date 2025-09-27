import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import ChatScreen from './src/screens/ChatScreen';
import { THEME_CONFIG } from './src/constants/Config';

export default function App() {
  return (
    <SafeAreaProvider>
      <ChatScreen />
      <StatusBar
        style="dark"
        backgroundColor={THEME_CONFIG.colors.background}
      />
    </SafeAreaProvider>
  );
}
