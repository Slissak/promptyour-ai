# API Chat Types Analysis

## Current State

### ✅ Type 1: Quick One-Liner
**Endpoint**: `POST /api/v1/chat/quick`
**Implementation**: ✅ EXISTS
**System Prompt**: Constant template (`quick_response_prompt.j2`)
**Features**:
- Uses fast model (claude-3-haiku)
- Max 100 tokens
- Temperature 0.3 (direct answers)
- Includes conversation history
- Specialized system prompt for concise responses

**Request Schema**: `QuickInput`
```python
{
    "question": str,
    "conversation_id": Optional[str],
    "message_history": Optional[List[Message]],
    "force_model": Optional[str],
    "force_provider": Optional[str]
}
```

**Response Schema**: `QuickResponse`
```python
{
    "content": str,
    "model_used": str,
    "provider": str,
    "message_id": str,
    "cost": float,
    "response_time_ms": int,
    "system_prompt": str
}
```

---

### ❌ Type 2: RAW Answer
**Endpoint**: ❌ DOES NOT EXIST AS STANDALONE
**Current Status**: Generated inside `/chat/message` as part of comparison
**Required Behavior**:
- NO system prompt (empty string)
- ONLY user question
- NO context, NO theme, NO audience
- NO conversation history

**What Exists Now**:
- RAW response is generated in `chat_service.py` lines 150-171
- Returned as `raw_response` field in ChatResponse
- But requires calling the enhanced endpoint

**What's Missing**:
- Standalone `/chat/raw` endpoint
- Ability to get RAW response without enhanced response

---

### ✅ Type 3: Enhanced
**Endpoint**: `POST /api/v1/chat/message`
**Implementation**: ✅ EXISTS
**System Prompt**: Dynamic, generated based on theme/audience/style
**Features**:
- User question + conversation history
- Enhanced system prompt with:
  - Theme-specific expert persona
  - Audience psychology adaptation
  - Response style preferences
  - Context integration
- Max 4000 tokens
- Temperature 0.7
- **Also generates RAW response** for comparison

**Request Schema**: `UserInput`
```python
{
    "question": str,
    "theme": str,  # 9 options
    "audience": str,  # 6 options
    "response_style": Optional[str],  # 4 options
    "context": Optional[str],
    "conversation_id": Optional[str],
    "message_history": Optional[List[Message]],
    "force_model": Optional[str],
    "force_provider": Optional[str]
}
```

**Response Schema**: `ChatResponse`
```python
{
    "content": str,  # Enhanced response
    "model_used": str,
    "provider": str,
    "message_id": str,
    "cost": float,
    "response_time_ms": int,
    "reasoning": str,
    "system_prompt": str,  # Enhanced system prompt
    "raw_response": Optional[str]  # RAW for comparison
}
```

---

## Gap Analysis

### ❌ Missing: Standalone RAW Endpoint

**Required**: `POST /api/v1/chat/raw`

**Purpose**: Allow users to get ONLY the RAW model response without any prompt engineering

**Request Schema**: Should be similar to `QuickInput` but simpler
```python
class RawInput(BaseModel):
    question: str
    conversation_id: Optional[str] = None
    force_model: Optional[str] = None
    force_provider: Optional[str] = None
    # NO message_history - truly raw
```

**Response Schema**: Should be similar to `QuickResponse`
```python
class RawResponse(BaseModel):
    content: str
    model_used: str
    provider: str
    message_id: str
    cost: float
    response_time_ms: int
    system_prompt: str  # Will always be empty ""
```

**Implementation Requirements**:
1. Create `RawInput` and `RawResponse` schemas in `models/schemas.py`
2. Add `process_raw_request()` method to `ChatService`
3. Add `/raw` route to `api/v1/routes/chat.py`
4. Ensure NO system prompt (empty string)
5. Ensure NO conversation history
6. Just send the user question directly to the model

---

## Summary

| Chat Type | Endpoint | Exists? | System Prompt | History | Theme/Audience |
|-----------|----------|---------|---------------|---------|----------------|
| Quick One-Liner | `/chat/quick` | ✅ YES | Constant template | ✅ YES | ❌ NO |
| RAW Answer | `/chat/raw` | ❌ **NO** | Empty ("") | ❌ NO | ❌ NO |
| Enhanced | `/chat/message` | ✅ YES | Dynamic (theme+audience) | ✅ YES | ✅ YES |

**Action Required**: Implement standalone `/chat/raw` endpoint
