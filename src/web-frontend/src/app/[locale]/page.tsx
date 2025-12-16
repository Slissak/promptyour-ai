import { getTranslations } from 'next-intl/server';
import Link from 'next/link';
import { HomeHeader } from '@/components/layout/HomeHeader';

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
        <HomeHeader locale={locale} title={t('chat.title')} />

        {/* Apps Grid */}
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto mb-12">
          {/* PromptYour.AI Card */}
          <div className="bg-white p-8 rounded-xl shadow-md hover:shadow-lg transition-shadow border border-gray-100 flex flex-col items-center text-center">
            <div className="w-16 h-16 bg-primary-100 text-primary-600 rounded-2xl flex items-center justify-center mb-6 text-3xl">
              💬
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              {t('apps.promptyourai.name')}
            </h2>
            <p className="text-gray-600 mb-8 flex-grow">
              {t('apps.promptyourai.description')}
            </p>
            <Link
              href={`/${locale}/chat`}
              className="w-full bg-primary-600 hover:bg-primary-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              {t('apps.promptyourai.action')}
            </Link>
          </div>

          {/* VisGuiAI Card */}
          <div className="bg-white p-8 rounded-xl shadow-md hover:shadow-lg transition-shadow border border-gray-100 flex flex-col items-center text-center">
            <div className="w-16 h-16 bg-indigo-100 text-indigo-600 rounded-2xl flex items-center justify-center mb-6 text-3xl">
              🎨
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              {t('apps.visguiai.name')}
            </h2>
            <p className="text-gray-600 mb-8 flex-grow">
              {t('apps.visguiai.description')}
            </p>
            <a
              href="#" // Placeholder for external repo/app URL
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            >
              {t('apps.visguiai.action')}
            </a>
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