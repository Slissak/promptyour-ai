# LM Studio Integration Guide

This guide explains how to set up and use LM Studio for local LLM inference with the PromptYour.AI backend.

## Overview

The PromptYour.AI backend now supports **local LLM inference** through LM Studio integration, providing:

- ✅ **Free local inference** - No API costs
- ✅ **Complete privacy** - Data never leaves your machine  
- ✅ **No rate limits** - Use as much as you want
- ✅ **Offline capability** - Works without internet
- ✅ **Fast GPU acceleration** - Optimized performance
- ✅ **Automatic fallback** - Falls back to OpenRouter if needed

## Quick Start

### 1. Install LM Studio

1. Download LM Studio from https://lmstudio.ai/
2. Install and launch the application
3. The application is available for Windows, macOS, and Linux

### 2. Download a Model

1. In LM Studio, go to the "Search" tab
2. **Recommended models for different use cases:**
   - **Fast & Lightweight**: `Llama 3.2 3B` (3GB RAM)
   - **Balanced**: `Llama 3.1 8B` (8GB RAM) 
   - **High Quality**: `Llama 3.1 70B` (requires 32GB+ RAM)
   - **Code Generation**: `Code Llama 7B` or `Qwen 2.5 Coder`
   - **Ultra Fast**: `Phi-3 Mini` (2GB RAM)

3. Click download on your preferred model
4. Wait for download to complete

### 3. Load the Model

1. Go to the "Chat" tab in LM Studio
2. Select your downloaded model from the dropdown
3. Click "Load Model"
4. Wait for the model to load (you'll see GPU/CPU usage indicators)

### 4. Start the Local Server

1. Go to the "Local Server" tab in LM Studio
2. Click "Start Server"
3. The server will start on `http://localhost:1234` by default
4. You should see "Server running" status

### 5. Configure Backend (Optional)

The backend is already configured to use LM Studio by default. If you need to customize:

```env
# .env file
LM_STUDIO_URL=http://localhost:1234/v1
PREFERRED_LLM_PROVIDER=auto  # or "lm_studio" to force local
PREFER_LOCAL_LLM=true
```

### 6. Test the Integration

Run the test script to verify everything is working:

```bash
python test_lm_studio_integration.py
```

You should see output like:
```
✅ LM Studio is running!
✅ Provider integration test successful!
   Provider used: lm_studio
   Model used: test-model (via llama-3.2-3b)
   Cost: $0.000000
```

## Using the Backend

### Automatic Provider Selection

The backend automatically chooses the best available provider:

1. **LM Studio** (if running and model loaded) - Preferred for privacy and cost
2. **OpenRouter** (if API key configured) - Fallback for cloud models

### API Endpoints

#### Check Provider Status
```bash
curl http://localhost:8000/api/v1/providers/status
```

#### List Available Models
```bash  
curl http://localhost:8000/api/v1/providers/models
```

#### Get Setup Recommendations
```bash
curl http://localhost:8000/api/v1/providers/setup-guide
```

#### Test Integration
```bash
curl -X POST http://localhost:8000/api/v1/providers/test
```

#### Troubleshoot Issues
```bash
curl http://localhost:8000/api/v1/providers/troubleshoot
```

### WebSocket Chat

The real-time WebSocket chat automatically uses your local LM Studio model:

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/chat?user_id=test_user');

ws.send(JSON.stringify({
    type: 'chat_request',
    data: {
        question: 'Hello from local LLM!',
        theme: 'general_questions',
        context: 'Testing local inference'
    }
}));
```

## Model Recommendations

### For Different RAM Sizes

| RAM Available | Recommended Model | Use Case |
|---------------|-------------------|----------|
| 4-8GB | Phi-3 Mini (2GB) | Ultra-fast responses |
| 8-16GB | Llama 3.2 3B | Balanced speed/quality |
| 16-32GB | Llama 3.1 8B | High quality responses |
| 32GB+ | Llama 3.1 70B | Best possible quality |

### For Different Tasks

| Task | Recommended Model |
|------|-------------------|
| **Code Generation** | Code Llama 7B, Qwen 2.5 Coder |
| **Creative Writing** | Llama 3.1 8B/70B |
| **Academic Help** | Llama 3.2 3B/8B |
| **General Chat** | Llama 3.2 3B |
| **Business/Professional** | Llama 3.1 8B |

## Troubleshooting

### LM Studio Not Detected

**Problem**: "LM Studio is not running" message

**Solutions**:
1. Make sure LM Studio is installed and running
2. Check that a model is loaded in the Chat tab
3. Verify the Local Server is started
4. Check if port 1234 is available
5. Restart LM Studio if needed

### Model Loading Issues

**Problem**: Model fails to load or runs out of memory

**Solutions**:
1. Choose a smaller model for your RAM size
2. Close other memory-intensive applications
3. Enable GPU acceleration in LM Studio settings
4. Consider using quantized models (Q4, Q8)

### Slow Inference

**Problem**: Responses take too long

**Solutions**:
1. Enable GPU acceleration in LM Studio
2. Use a smaller, faster model (Phi-3 Mini, Llama 3.2 3B)
3. Check CPU/GPU usage in LM Studio
4. Reduce max_tokens in requests
5. Close other applications using GPU/CPU

### Connection Issues

**Problem**: Backend can't connect to LM Studio

**Solutions**:
1. Check LM Studio Local Server tab shows "Server running"
2. Test direct connection: `curl http://localhost:1234/v1/models`
3. Check firewall settings allow localhost connections
4. Restart both LM Studio and the backend
5. Check LM_STUDIO_URL in .env file

## Configuration Options

### Environment Variables

```env
# LM Studio Configuration
LM_STUDIO_URL=http://localhost:1234/v1        # LM Studio server URL
LM_STUDIO_API_KEY=lm-studio                   # API key (usually not needed)
PREFERRED_LLM_PROVIDER=auto                   # auto|lm_studio|openrouter  
PREFER_LOCAL_LLM=true                         # Prefer local over cloud
```

### Provider Selection Logic

1. **`PREFERRED_LLM_PROVIDER=auto`** (default):
   - Use LM Studio if healthy and `PREFER_LOCAL_LLM=true`
   - Fall back to OpenRouter if LM Studio unavailable
   - Fall back to LM Studio if OpenRouter fails

2. **`PREFERRED_LLM_PROVIDER=lm_studio`**:
   - Always try LM Studio first
   - Only use OpenRouter if LM Studio completely unavailable

3. **`PREFERRED_LLM_PROVIDER=openrouter`**:
   - Always use OpenRouter
   - Never use LM Studio (unless OpenRouter fails)

## Benefits of Local LLM

### Privacy & Security
- All data stays on your local machine
- No API calls to external services
- Complete control over your data
- GDPR/compliance friendly

### Cost & Performance
- Zero API costs for inference
- No rate limits or usage quotas
- Predictable response times
- No dependency on external services

### Customization
- Load any compatible model
- Fine-tune models for your use case
- Control inference parameters
- Experiment with different architectures

## Advanced Usage

### Multiple Models

You can switch models in LM Studio without restarting the backend:

1. Stop the current model in LM Studio
2. Load a different model 
3. The backend will automatically detect the new model
4. No backend restart required

### GPU Acceleration

For best performance, enable GPU acceleration:

1. In LM Studio Settings > Hardware
2. Select your GPU (NVIDIA, Apple Silicon, etc.)
3. Enable GPU acceleration
4. Reload your model to use GPU

### Custom Server Port

If you need to use a different port:

1. In LM Studio Local Server settings, change the port
2. Update your `.env` file:
   ```env
   LM_STUDIO_URL=http://localhost:YOUR_PORT/v1
   ```
3. Restart the backend

## Support

If you encounter issues:

1. Run the diagnostic endpoint:
   ```bash
   curl http://localhost:8000/api/v1/providers/troubleshoot
   ```

2. Check the backend logs for error messages

3. Verify LM Studio is working independently:
   ```bash
   curl http://localhost:1234/v1/models
   ```

4. Try the test integration:
   ```bash
   python test_lm_studio_integration.py
   ```

For more help, check the LM Studio documentation at https://docs.lmstudio.ai/