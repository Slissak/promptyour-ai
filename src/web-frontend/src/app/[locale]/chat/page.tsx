import { useTranslations } from 'next-intl';
import { getTranslations } from 'next-intl/server';
import { LanguageSelector } from '@/components/layout/LanguageSelector';
import { TwoTierChat } from '@/components/chat/TwoTierChat';

export default function ChatPage({
  params: { locale }
}: {
  params: { locale: string }
}) {
  const t = useTranslations();

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8 h-screen flex flex-col">
        {/* Header */}
        <header className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {t('chat.title')}
            </h1>
            <p className="text-gray-600 text-sm">
              {t('chat.subtitle')}
            </p>
          </div>
          <LanguageSelector />
        </header>

        {/* Chat Interface */}
        <div className="flex-1 bg-white rounded-lg shadow-sm overflow-hidden">
          <TwoTierChat locale={locale} />
        </div>
      </div>
    </main>
  );
}

export async function generateMetadata({
  params: { locale }
}: {
  params: { locale: string }
}) {
  const t = await getTranslations({ locale });

  return {
    title: t('chat.title'),
    description: t('chat.subtitle'),
  };
}