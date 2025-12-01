import { NextIntlClientProvider, hasLocale } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { routing } from '@/i18n/routing';
import { isRTL } from '@/i18n/config';
import clsx from 'clsx';
import '../globals.css';

import { Providers } from './providers';

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

export default async function LocaleLayout({
  children,
  params: { locale }
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  // Ensure that the incoming `locale` is valid
  if (!routing.locales.includes(locale)) {
    notFound();
  }

  const messages = await getMessages();

  const direction = isRTL(locale) ? 'rtl' : 'ltr';
  const fontClass = locale === 'ar' ? 'font-arabic' :
                   locale === 'he' ? 'font-hebrew' :
                   'font-english';

  return (
    <html lang={locale} dir={direction}>
      <body className={clsx(fontClass, direction)}>
        <Providers locale={locale} messages={messages}>
          {children}
        </Providers>
      </body>
    </html>
  );
}