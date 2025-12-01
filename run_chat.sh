#!/bin/bash
# Terminal Chat Runner for PromptYour.AI

echo "🚀 Setting up Terminal Chat for PromptYour.AI..."

# Activate virtual environment
source .venv/bin/activate

# Install dependencies from requirements.txt
uv pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install packages. Please run manually:"
    echo "uv pip install -r requirements.txt"
    exit 1
fi

echo "✅ Dependencies ready!"
echo ""
echo "🤖 Starting Terminal Chat..."
echo "💡 Make sure the backend is running on http://localhost:8000"
echo ""
echo "📝 Usage: $0 [--quick] [--debug] [--api URL] [--http-only]"
echo "   --quick     Quick mode: skip theme and context questions"
echo "   --debug     Enable debug mode to show final prompts"
echo "   --api       Backend API URL (default: http://localhost:8000)"
echo "   --http-only Use HTTP only (no WebSocket)"
echo ""
echo "💡 Default: Enhanced mode with theme selection for better results"
echo "💡 Use --quick for faster responses without customization"
echo "🧠 NEW: Continuous chat with memory - after first message, context is remembered!"
echo "🔄 NEW: Use /new command to start fresh conversations anytime"
echo ""

# Run the chat
python3 terminal_chat.py "$@"