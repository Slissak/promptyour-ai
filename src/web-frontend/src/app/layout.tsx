import { Inter } from 'next/font/google';
import { locales } from '@/i18n/config';
import { notFound } from 'next/navigation';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'PromptYour.AI - Enhanced AI Chat',
  description: 'Enhanced AI responses through intelligent model routing with multi-language support',
};

// Generate static params for all supported locales
export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
      </body>
    </html>
  );
}