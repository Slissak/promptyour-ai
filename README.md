# PromptYour.AI - Cross-Platform Two-Tier Chat System

A comprehensive AI chat application with intelligent model routing, theme-based responses, and cross-platform support.

## 🌟 Features

### Two-Tier Chat System
- **Quick Responses**: Fast one-liner answers for immediate feedback
- **Enhanced Responses**: Detailed, theme-aware responses with audience targeting
- **Theme Selection**: 9 specialized themes (coding, creative, business, etc.)
- **Audience Targeting**: 6 audience levels (kids to professionals)
- **Conversation History**: Persistent across all question types

### Cross-Platform Support
- 🌐 **Web Interface**: Modern responsive React/Next.js interface
- 📱 **Mobile Apps**: Native iOS/Android apps via React Native/Expo
- 💻 **Terminal Interface**: Command-line interface for developers
- 🔄 **Shared Library**: 95% code reuse between platforms

### Multi-Language Support
- English, Arabic, Hebrew with RTL support
- Internationalization via next-intl
- Language-specific fonts and layouts

## 🏗️ Architecture

```
promp_your_ai/
├── src/
│   ├── backend/          # FastAPI backend with WebSocket support
│   ├── web-frontend/     # Next.js web interface
│   ├── mobile-frontend/  # React Native/Expo mobile app
│   └── shared/           # Shared TypeScript API client library
├── tests/                # Comprehensive test suite
├── evaluations/          # Evaluation framework
└── docs/                 # Documentation
```

### Technology Stack
- **Backend**: Python, FastAPI, WebSocket, Pydantic, UV package manager
- **Web**: Next.js 15, TypeScript, Tailwind CSS, next-intl
- **Mobile**: React Native, Expo SDK 54, TypeScript
- **Shared**: TypeScript, Axios HTTP client, conversation management

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- UV package manager
- Expo CLI (for mobile development)

### 1. Backend Setup
```bash
# Create virtual environment
uv venv .venv
source .venv/bin/activate

# Install dependencies
make install-dev

# Start backend server
make run-backend
# Backend runs on http://localhost:8001
```

### 2. Web Frontend Setup
```bash
cd src/web-frontend
npm install
npm run dev
# Web interface runs on http://localhost:3000
```

### 3. Mobile App Setup
```bash
cd src/mobile-frontend
npm install
npm start
# Expo dev server runs on http://localhost:8081
```

### 4. Terminal Chat (Optional)
```bash
# Quick one-liner mode
python terminal_chat.py --api http://localhost:8001 --quick

# Full interactive mode
python terminal_chat.py --api http://localhost:8001
```

## 📱 Platform Access

| Platform | URL | Features |
|----------|-----|----------|
| **Web Interface** | http://localhost:3000/en/chat | Responsive design, RTL support |
| **Mobile App** | Expo Go app + QR code | Native mobile experience |
| **Terminal** | Command line | Developer-friendly CLI |
| **API** | http://localhost:8001/docs | FastAPI interactive docs |

## 🔧 Development Commands

### Backend
```bash
make test              # Run all tests with coverage
make lint              # Run flake8 linting
make format            # Format code with black
make type-check        # Run mypy type checking
```

### Frontend
```bash
# Web
cd src/web-frontend
npm run build          # Build for production
npm run lint           # ESLint checking
npm run type-check     # TypeScript checking

# Mobile
cd src/mobile-frontend
npm run build          # Build for production
expo build:ios         # Build iOS app
expo build:android     # Build Android app
```

## 🌐 Two-Tier Chat Workflow

1. **User Input**: Submit question through any platform
2. **Quick Response**: Receive fast one-liner answer immediately
3. **Enhancement Option**: Choose to get detailed response
4. **Theme/Audience Selection**: Customize response style and complexity
5. **Enhanced Response**: Receive detailed, theme-aware answer
6. **History Preservation**: All interactions saved with context

### API Endpoints

- `POST /api/v1/chat/quick` - Quick one-liner responses
- `POST /api/v1/chat/enhanced` - Detailed theme-based responses
- `GET /api/v1/providers/status` - Provider health monitoring
- `WebSocket /ws/chat` - Real-time chat (future feature)

## 🎯 Themes Available

1. **Coding & Technical** - Programming, debugging, architecture
2. **Creative Writing** - Storytelling, poetry, creative content
3. **Business & Professional** - Strategy, analysis, presentations
4. **Educational** - Learning, tutorials, explanations
5. **Health & Wellness** - Fitness, nutrition, mental health
6. **Science & Research** - Scientific explanations, research
7. **Travel & Culture** - Travel guides, cultural insights
8. **Finance & Economics** - Financial advice, market analysis
9. **General** - Balanced, versatile responses

## 👥 Audience Levels

- **Kids (5-10)** - Simple, fun explanations
- **Teens (13-17)** - Age-appropriate, engaging content
- **College Students** - Academic level, detailed explanations
- **General Adults** - Balanced complexity and detail
- **Professionals** - Industry-specific, advanced content
- **Experts** - Technical, comprehensive, specialized

## 🔐 Environment Setup

Create `.env` files in respective directories:

### Backend (.env)
```env
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GROQ_API_KEY=your_groq_key
OPENROUTER_API_KEY=your_openrouter_key
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8001
```

## 🧪 Testing

### Backend Tests
```bash
make test-unit         # Unit tests only
make test-integration  # Integration tests only
make test-e2e          # End-to-end tests only
```

### Frontend Tests
```bash
# Web
cd src/web-frontend
npm test

# Mobile
cd src/mobile-frontend
npm test
```

## 🚀 Deployment

### Web Frontend
```bash
cd src/web-frontend
npm run build
npm start
```

### Mobile Apps
```bash
cd src/mobile-frontend
expo build:ios
expo build:android
```

### Backend
```bash
make run-backend
# or for production:
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## 📊 Project Status

- ✅ **Backend API**: Complete with two-tier chat system
- ✅ **Web Interface**: Full Next.js implementation with i18n
- ✅ **Mobile Apps**: React Native/Expo implementation
- ✅ **Shared Library**: TypeScript API client with 95% code reuse
- ✅ **Terminal Interface**: CLI for developers
- ✅ **Testing**: Comprehensive test coverage
- ✅ **Documentation**: Complete setup and usage guides

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests: `make test`
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Documentation**: Check the `/docs` directory
- **API Docs**: http://localhost:8001/docs
- **Issues**: GitHub Issues
- **Chat Interface**: Test at http://localhost:3000/en/chat

---

**Built with ❤️ for intelligent conversation across all platforms**