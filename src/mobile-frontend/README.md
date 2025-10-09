# PromptYour.AI Frontend

Cross-platform frontend application for PromptYour.AI - built with React Native, Expo, and TypeScript.

## Features

- **Cross-Platform**: Runs on iOS, Android, and Web with 95%+ code sharing
- **Real-Time Chat**: WebSocket support for real-time messaging with fallback to REST API
- **Multiple Chat Modes**:
  - **Regular**: Full customization with theme, audience, and response style
  - **Quick**: Fast responses without configuration
  - **Raw**: Direct model responses without prompt engineering (for comparison)
- **Rich Configuration**: Theme selection, audience targeting, response style customization
- **Persistent Storage**: Saves preferences and conversation history locally
- **Responsive Design**: Optimized for mobile, tablet, and desktop

## Tech Stack

- **Framework**: Expo SDK 52 with React Native 0.76
- **Navigation**: Expo Router (file-based routing)
- **State Management**: Zustand
- **UI Components**: React Native Paper
- **API**: Fetch API + WebSocket
- **Storage**: AsyncStorage
- **TypeScript**: Full type safety

## Prerequisites

- Node.js 18+ and npm
- Expo CLI
- Backend API running (see main README)

## Installation

```bash
cd frontend-app
npm install
```

## Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Update the API URLs in `.env`:
```env
EXPO_PUBLIC_API_URL=http://localhost:8001
EXPO_PUBLIC_WS_URL=ws://localhost:8001
```

## Development

### Web
```bash
npm run web
```
Opens at http://localhost:8081

### iOS Simulator
```bash
npm run ios
```

### Android Emulator
```bash
npm run android
```

### Development Server
```bash
npm start
```
Then scan QR code with Expo Go app

## Project Structure

```
frontend-app/
├── app/                      # Expo Router screens
│   ├── (tabs)/              # Tab-based navigation
│   │   ├── chat.tsx         # Main chat screen
│   │   ├── settings.tsx     # Settings screen
│   │   └── _layout.tsx      # Tab layout
│   └── _layout.tsx          # Root layout
├── components/              # Reusable UI components
│   ├── chat/               # Chat-related components
│   │   ├── ChatBubble.tsx
│   │   ├── MessageList.tsx
│   │   └── InputBar.tsx
│   └── config/             # Configuration components
│       ├── ModeSwitch.tsx
│       ├── ThemeSelector.tsx
│       ├── AudienceSelector.tsx
│       ├── StyleSelector.tsx
│       └── ConfigPanel.tsx
├── services/               # API and business logic
│   ├── api.ts             # REST API client
│   ├── websocket.ts       # WebSocket manager
│   └── storage.ts         # Local persistence
├── hooks/                  # Custom React hooks
│   └── useChat.ts         # Chat functionality hook
├── store/                  # Zustand state stores
│   ├── chatStore.ts       # Chat state
│   ├── configStore.ts     # Config state
│   └── userStore.ts       # User state
└── types/                  # TypeScript definitions
    └── api.ts             # API types matching backend

```

## Building for Production

### Web
```bash
npx expo export --platform web
```
Output in `dist/` directory

### iOS
```bash
eas build --platform ios
```

### Android
```bash
eas build --platform android
```

## Features in Detail

### Chat Interface
- WhatsApp/iMessage-style chat bubbles
- User messages on right, AI responses on left
- Typing indicators during processing
- Message timestamps and model info
- Long-press to copy messages

### Configuration Panel
- **Mode Toggle**: Switch between Regular, Quick, and Raw modes
- **Theme Dropdown**: Academic, Creative Writing, Coding, Business, etc.
- **Audience Selector**: Small Kids to Professionals
- **Response Style**: Brief, Detailed, Instructions Only, or Comprehensive
- **Context Input**: Optional additional context field

### Settings
- View User ID
- Configure backend URL
- Clear chat history
- Reset configuration
- View app info

## API Integration

The frontend connects to the backend API at the configured `EXPO_PUBLIC_API_URL`:

- **REST API**: `/api/v1/chat/message`, `/api/v1/chat/quick`, `/api/v1/chat/raw`
- **WebSocket**: `/api/v1/ws/chat` for real-time communication

## State Management

Uses Zustand for simple, performant state management:

- **chatStore**: Manages messages, conversation state, loading states
- **configStore**: Manages user configuration (theme, audience, style)
- **userStore**: Manages user ID and initialization

## Troubleshooting

### Cannot connect to backend
- Check that backend is running on correct port
- Verify `.env` file has correct API URLs
- For iOS simulator: Use `http://localhost:8001`
- For Android emulator: Use `http://10.0.2.2:8001`
- For physical device: Use your computer's IP address

### WebSocket connection fails
- WebSocket URL should use `ws://` (or `wss://` for HTTPS)
- Make sure backend WebSocket endpoint is accessible
- App will fall back to REST API if WebSocket fails

### Type errors
- Run `npx tsc --noEmit` to check TypeScript errors
- Ensure all dependencies are installed

## License

Part of PromptYour.AI project
