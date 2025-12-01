'use client';

import { useState } from 'react';
import { createClient } from '@/lib/supabase/client';
import { SessionContextProvider } from '@supabase/auth-helpers-react';
import { NextIntlClientProvider } from 'next-intl';
import { UserModeProvider } from '@/context/UserModeContext';

export function Providers({ children, messages, locale }: { children: React.ReactNode, messages: any, locale: string }) {
  const [supabaseClient] = useState(() => createClient());

  return (
    <SessionContextProvider supabaseClient={supabaseClient}>
      <NextIntlClientProvider locale={locale} messages={messages}>
        <UserModeProvider>
          {children}
        </UserModeProvider>
      </NextIntlClientProvider>
    </SessionContextProvider>
  );
}
