import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { locales, isRTL } from '@/i18n/config';
import clsx from 'clsx';

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

export default async function LocaleLayout({
  children,
  params: { locale }
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  // Validate that the incoming `locale` parameter is valid
  if (!locales.includes(locale as any)) {
    notFound();
  }

  // Providing all messages to the client
  // side is the easiest way to get started
  const messages = await getMessages();

  const direction = isRTL(locale) ? 'rtl' : 'ltr';
  const fontClass = locale === 'ar' ? 'font-arabic' :
                   locale === 'he' ? 'font-hebrew' :
                   'font-english';

  return (
    <html lang={locale} dir={direction}>
      <body className={clsx(fontClass, direction)}>
        <NextIntlClientProvider messages={messages}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}