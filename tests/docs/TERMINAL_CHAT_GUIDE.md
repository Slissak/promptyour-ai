# Terminal Chat Interface Guide

A beautiful, interactive terminal-based chat interface for testing the PromptYour.AI backend.

## 🚀 Quick Start

### 1. Start the Backend

```bash
# Option 1: Using the environment setup
PYTHONPATH=src/backend python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Option 2: If you have make configured
make run-backend
```

### 2. Start the Terminal Chat

```bash
# Option 1: Simple start
python terminal_chat.py

# Option 2: Using the convenience script
./run_chat.sh

# Option 3: With custom API URL
python terminal_chat.py --api http://localhost:8000

# Option 4: HTTP-only mode (no WebSocket)
python terminal_chat.py --http-only
```

## 📦 Dependencies

The chat interface requires these packages:
```bash
pip install httpx websockets rich
```

These will be automatically installed when you run `./run_chat.sh`.

## 🎯 Features

### ✨ **Interactive Chat**
- Real-time responses via WebSocket
- Beautiful terminal UI with colors and formatting
- Automatic fallback to HTTP if WebSocket fails

### 🎨 **Rich Interface**
- Colorful, formatted output
- Progress indicators during processing
- Markdown rendering for AI responses
- Interactive prompts and menus

### 🔧 **Provider Integration**
- Automatic detection of LM Studio and OpenRouter
- Real-time provider status display
- Shows which model and provider was used
- Cost tracking per message

### 📊 **Session Management**
- Conversation history within session
- Session statistics (cost, response times, providers used)
- Message rating system

## 🎮 Usage

### Basic Chat
Just type your question and press Enter:
```
> What is Python?
```

### Theme Selection
For better results, you can specify themes:
1. Academic Help
2. Creative Writing  
3. Coding/Programming
4. Business/Professional
5. Personal Learning
6. Research/Analysis
7. Problem Solving
8. Tutoring/Education
9. General Questions

### Commands
- `/help` - Show help information
- `/status` - Check backend and provider status
- `/stats` - Show session statistics
- `/clear` - Clear screen
- `/quit` or `/exit` - Exit chat

### Example Session
```
> Hello, can you help me with Python?

🎯 Customize theme and context for better results? [y/N]: y

💭 Your question: Hello, can you help me with Python?

📋 Available themes:
   1. Academic Help
   2. Creative Writing
   3. Coding Programming    ← Choose this for Python questions
   ...

🎯 Choose theme (1-9, or press Enter for general): 3

📝 Additional context (optional): I'm a beginner learning basic syntax

[Processing with spinner animation...]

🤖 AI Response:
[Formatted markdown response with syntax highlighting]

🤖 Model: claude-3-haiku (via qwen/qwen3-4b-2507)
🏠 Provider: lm_studio
💰 Cost: $0.000000
⏱️  Response Time: 2341ms

⭐ Rate this response (1-5, or press Enter to skip): 5
✅ Rating submitted: 5/5
```

## 🔌 Backend Connection

The chat connects to your backend at `http://localhost:8000` by default.

**Status Indicators:**
- ✅ Green: Provider healthy and ready
- ❌ Red: Provider unavailable or error
- ⚠️ Yellow: Provider partially available

**Provider Information:**
- **LM Studio**: Shows loaded model if available
- **OpenRouter**: Shows API key status

## 🎨 Interface Features

### **Welcome Screen**
```
╔═══════════════════════════════════════════════════════════╗
║              🤖 PromptYour.AI Terminal Chat               ║
║                                                           ║
║  Enhanced AI responses through intelligent model routing  ║
╚═══════════════════════════════════════════════════════════╝

🔌 Provider Status
┏━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Provider    ┃ Status  ┃ Details                      ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Lm Studio   │ healthy │ Model: qwen/qwen3-4b-2507    │
│ Openrouter  │ healthy │ API Key: ✅                   │
└─────────────┴─────────┴──────────────────────────────────┘
```

### **Response Display**
- **Metadata Table**: Model, provider, cost, timing
- **Formatted Response**: Markdown with syntax highlighting
- **Interactive Rating**: 1-5 star rating system

### **Session Statistics**
```
📊 Session Statistics
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric           ┃ Value                         ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Total Messages   │ 5                             │
│ Total Cost       │ $0.000000                     │
│ Avg Response Time│ 2841ms                        │
│ Most Used Provider│ lm_studio                     │
│ Most Used Model  │ qwen/qwen3-4b-2507            │
└──────────────────┴───────────────────────────────────────┘
```

## 🐛 Troubleshooting

### Backend Not Running
```
❌ Cannot connect to backend. Make sure it's running!
```
**Solution**: Start the backend first:
```bash
PYTHONPATH=src/backend python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Missing Dependencies
```
Missing required packages. Please install them:
pip install httpx websockets rich
```
**Solution**: Install the required packages or use `./run_chat.sh`

### WebSocket Connection Failed
The chat will automatically fall back to HTTP mode if WebSocket fails.

### LM Studio Not Detected
- Make sure LM Studio is running
- Check that a model is loaded
- Verify the local server is started on port 1234

## 🎯 Pro Tips

### **For Best Results:**
1. **Use specific themes** - Choose the most relevant theme for your question
2. **Add context** - Provide background information when helpful  
3. **Try different models** - Switch models in LM Studio to see different responses
4. **Rate responses** - Help improve the system by rating answers

### **Performance:**
- **Local models** (LM Studio) are free but may be slower
- **Cloud models** (OpenRouter) are faster but cost money
- The system automatically chooses the best available option

### **Advanced Usage:**
```bash
# Use different API endpoint
python terminal_chat.py --api http://192.168.1.100:8000

# Force HTTP mode for debugging
python terminal_chat.py --http-only

# Run with verbose output
python terminal_chat.py -v
```

## 🔧 Configuration

The chat interface reads the same configuration as the backend:
- **LM Studio URL**: Automatically detected at `http://localhost:1234`
- **Provider Preferences**: Uses backend's `PREFER_LOCAL_LLM` setting
- **Model Selection**: Based on theme and backend's model selector

## 📝 Notes

- **Conversation Persistence**: Currently within session only
- **History**: Each session generates a unique conversation ID
- **Ratings**: Collected but require backend storage implementation
- **Offline Mode**: Works with LM Studio when internet unavailable

The terminal chat provides a full-featured way to test and interact with your PromptYour.AI backend, showcasing all the intelligent routing, model selection, and provider integration features in a beautiful, user-friendly interface.