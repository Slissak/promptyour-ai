// Supported locales
export const locales = ['en', 'ar', 'he', 'es', 'fr', 'zh'] as const;
export const defaultLocale = 'en' as const;

export type Locale = (typeof locales)[number];

// RTL languages
export const rtlLocales = ['ar', 'he'] as const;

export function isRTL(locale: string): boolean {
  return rtlLocales.includes(locale as any);
}

export function getDirectionClass(locale: string): 'rtl' | 'ltr' {
  return isRTL(locale) ? 'rtl' : 'ltr';
}

export function getTextAlign(locale: string): string {
  return isRTL(locale) ? 'text-right' : 'text-left';
}