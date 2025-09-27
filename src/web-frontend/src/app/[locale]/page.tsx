import { getTranslations } from 'next-intl/server';
import Link from 'next/link';
import { LanguageSelector } from '@/components/layout/LanguageSelector';

export default async function HomePage({
  params
}: {
  params: Promise<{ locale: string }>
}) {
  const { locale } = await params;
  const t = await getTranslations();

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            {t('chat.title')}
          </h1>
          <LanguageSelector />
        </header>

        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-5xl font-bold text-gray-900 mb-4">
            PromptYour.AI
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            {t('chat.subtitle')}
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href={`/${locale}/chat`}
              className="bg-primary-500 hover:bg-primary-600 text-white px-8 py-3 rounded-lg font-medium transition-colors"
            >
              {t('nav.chat')}
            </Link>
            <Link
              href={`/${locale}/debug`}
              className="border border-primary-500 text-primary-500 hover:bg-primary-50 px-8 py-3 rounded-lg font-medium transition-colors"
            >
              {t('common.debug_mode')}
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          <div className="text-center p-6 bg-white rounded-lg shadow-sm">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              🎯
            </div>
            <h3 className="text-lg font-semibold mb-2">Smart Model Selection</h3>
            <p className="text-gray-600">Automatically chooses the best AI model for your specific question.</p>
          </div>

          <div className="text-center p-6 bg-white rounded-lg shadow-sm">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              👥
            </div>
            <h3 className="text-lg font-semibold mb-2">Audience-Aware</h3>
            <p className="text-gray-600">Tailors responses to your specific audience and context.</p>
          </div>

          <div className="text-center p-6 bg-white rounded-lg shadow-sm">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              🌍
            </div>
            <h3 className="text-lg font-semibold mb-2">Multi-Language</h3>
            <p className="text-gray-600">Supports multiple languages including RTL languages like Arabic and Hebrew.</p>
          </div>
        </div>
      </div>
    </main>
  );
}

export async function generateMetadata({
  params
}: {
  params: Promise<{ locale: string }>
}) {
  const { locale } = await params;
  const t = await getTranslations({ locale });

  return {
    title: t('chat.title'),
    description: t('chat.subtitle'),
  };
}