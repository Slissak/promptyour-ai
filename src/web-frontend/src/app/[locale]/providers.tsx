'use client';

import { NextIntlClientProvider } from 'next-intl';
import { UserModeProvider } from '@/context/UserModeContext';

export function Providers({ children, messages, locale }: { children: React.ReactNode, messages: any, locale: string }) {
  return (
    <NextIntlClientProvider locale={locale} messages={messages}>
      <UserModeProvider>
        {children}
      </UserModeProvider>
    </NextIntlClientProvider>
  );
}
