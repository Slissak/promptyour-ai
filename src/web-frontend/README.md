# PromptYour.AI Web Frontend

A modern, multi-lingual web interface for PromptYour.AI with complete RTL language support.

## ✨ Features

- **🌍 Multi-lingual Support**: 6 languages including RTL (Arabic, Hebrew)
- **🎯 Smart Model Selection**: Intelligent AI model routing
- **👥 Audience-Aware**: Tailored responses for different audiences
- **🔬 Debug Mode**: Compare enhanced vs raw model responses
- **📱 Responsive Design**: Works on desktop, tablet, and mobile
- **⚡ Modern Stack**: Next.js 14, TypeScript, Tailwind CSS

## 🌐 Supported Languages

| Language | Code | Direction | Status |
|----------|------|-----------|---------|
| English | `en` | LTR | ✅ |
| Arabic | `ar` | RTL | ✅ |
| Hebrew | `he` | RTL | ✅ |
| Spanish | `es` | LTR | ✅ |
| French | `fr` | LTR | ✅ |
| Chinese | `zh` | LTR | ✅ |

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Type checking
npm run type-check
```

The app will be available at [http://localhost:3000](http://localhost:3000)

## 📁 Project Structure

```
src/
├── app/
│   ├── [locale]/           # Locale-based routing
│   │   ├── layout.tsx      # Locale-aware layout
│   │   ├── page.tsx        # Home page
│   │   ├── chat/           # Chat interface
│   │   └── debug/          # Debug mode
├── components/
│   ├── ui/                 # Reusable UI components
│   ├── chat/               # Chat-specific components
│   └── layout/             # Layout components
├── i18n/
│   ├── config.ts           # i18n configuration
│   └── request.ts          # Server-side i18n
├── messages/               # Translation files
│   ├── en.json            # English
│   ├── ar.json            # Arabic
│   └── he.json            # Hebrew
└── lib/                   # Utilities and hooks
```

## 🎨 RTL Language Support

The app automatically detects RTL languages and applies appropriate styling:

- **Direction**: Automatic `dir="rtl"` for Arabic and Hebrew
- **Text Alignment**: Right-to-left text alignment
- **Layout**: Flipped layouts for RTL languages
- **Fonts**: Language-specific font families
- **Icons**: Proper positioning for RTL context

## 🔧 Technology Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS with RTL utilities
- **i18n**: next-intl
- **UI Components**: Radix UI primitives
- **Icons**: Lucide React

## 🌍 Adding New Languages

1. Add the locale to `src/i18n/config.ts`:
```typescript
export const locales = ['en', 'ar', 'he', 'es', 'fr', 'zh', 'your-locale'] as const;
```

2. Create translation file `src/messages/your-locale.json`

3. Add language name to `LanguageSelector.tsx`

4. For RTL languages, add to `rtlLocales` array

## 📱 Responsive Design

The interface adapts to all screen sizes:

- **Desktop**: Full-featured chat interface
- **Tablet**: Optimized layout for touch
- **Mobile**: Compact, touch-friendly UI

## 🔬 Debug Mode

Special debug interface showing:

- Model selection reasoning
- Performance metrics (cost, tokens, time)
- Side-by-side comparison of enhanced vs raw responses
- Full system prompts used

## 📝 Contributing

When adding new features:

1. Ensure RTL compatibility
2. Add appropriate translations
3. Test on multiple screen sizes
4. Follow TypeScript best practices

## 🚀 Deployment

The app is configured for easy deployment:

- **Vercel**: Recommended (zero-config)
- **Docker**: Production Dockerfile included
- **Static Export**: Supports static hosting

## 📄 License

MIT License - see LICENSE file for details