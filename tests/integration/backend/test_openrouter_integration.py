#!/usr/bin/env python3
"""
Test script to validate OpenRouter integration
Tests the complete pipeline with real API calls (if API key is available)
"""
import os
import sys
import asyncio
from unittest.mock import Mock, patch, AsyncMock

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'backend'))

from app.models.schemas import UserInput, ThemeType, LLMRequest
from app.services.chat_service import ChatService
from app.integrations.openrouter_provider import OpenRouterProvider


async def test_openrouter_provider_direct():
    """Test OpenRouter provider directly"""
    print("Testing OpenRouter Provider...")
    
    provider = OpenRouterProvider()
    
    # Test 1: Health check
    print("Testing health check...")
    health = await provider.health_check()
    print(f"Health check result: {health}")
    
    # Test 2: Get available models 
    print("\nTesting available models...")
    models = await provider.get_available_models()
    if models:
        print(f"Found {len(models.get('data', []))} models")
        # Show first few models
        for i, model in enumerate(models.get('data', [])[:5]):
            print(f"  {i+1}. {model.get('id')} - {model.get('name')}")
    
    # Test 3: Model call (with mock if no API key)
    print("\nTesting model call...")
    
    request = LLMRequest(
        model="claude-3-haiku",
        system_prompt="You are a helpful assistant that responds concisely.",
        user_message="What is 2+2? Answer in one word.",
        max_tokens=100,
        temperature=0.1
    )
    
    try:
        if provider.api_key and provider.api_key != "your_openrouter_key_here":
            # Real API call
            response = await provider.call_model(request)
            print(f"✅ Real API call successful!")
            print(f"   Model: {response.model}")
            print(f"   Content: {response.content[:100]}...")
            print(f"   Tokens used: {response.tokens_used}")
            print(f"   Cost: ${response.cost:.6f}")
            print(f"   Response time: {response.response_time_ms}ms")
        else:
            print("⚠️  No API key found, skipping real API call")
            
    except Exception as e:
        print(f"❌ API call failed: {e}")


async def test_complete_chat_pipeline():
    """Test complete chat pipeline"""
    print("\n" + "="*50)
    print("Testing Complete Chat Pipeline...")
    
    chat_service = ChatService()
    
    # Mock the LLM provider call if no API key
    if not chat_service.llm_provider.api_key or chat_service.llm_provider.api_key == "your_openrouter_key_here":
        print("⚠️  No API key - using mock LLM responses")
        
        # Mock the LLM provider
        mock_response = Mock()
        mock_response.content = "The answer is 4."
        mock_response.model = "claude-3-haiku"
        mock_response.provider = "openrouter"
        mock_response.tokens_used = 15
        mock_response.cost = 0.0001
        mock_response.response_time_ms = 250
        mock_response.message_id = "mock-msg-id-123"
        
        chat_service.llm_provider.call_model = AsyncMock(return_value=mock_response)
    
    # Test with different themes
    test_cases = [
        {
            "question": "What is 2+2?",
            "theme": ThemeType.ACADEMIC_HELP,
            "context": "Basic arithmetic for elementary school",
            "user_id": "test-user-1"
        },
        {
            "question": "Write a short story about a robot",
            "theme": ThemeType.CREATIVE_WRITING,
            "context": "Science fiction, 100 words",
            "user_id": "test-user-2"
        },
        {
            "question": "How do I sort a list in Python?",
            "theme": ThemeType.CODING_PROGRAMMING,
            "context": "Beginner level, show example",
            "user_id": "test-user-3"
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest Case {i+1}: {test_case['theme'].value}")
        print(f"Question: {test_case['question']}")
        
        user_input = UserInput(
            question=test_case["question"],
            theme=test_case["theme"],
            context=test_case["context"]
        )
        
        try:
            response = await chat_service.process_user_request(
                user_input=user_input,
                user_id=test_case["user_id"]
            )
            
            print(f"✅ Pipeline completed successfully!")
            print(f"   Model used: {response.model_used}")
            print(f"   Provider: {response.provider}")
            print(f"   Cost: ${response.cost:.6f}")
            print(f"   Response time: {response.response_time_ms}ms")
            print(f"   Reasoning: {response.reasoning}")
            print(f"   Response: {response.content[:150]}...")
            
        except Exception as e:
            print(f"❌ Pipeline failed: {e}")
            import traceback
            traceback.print_exc()


async def test_error_handling():
    """Test error handling scenarios"""
    print("\n" + "="*50)
    print("Testing Error Handling...")
    
    # Test with invalid API key
    provider = OpenRouterProvider()
    original_key = provider.api_key
    provider.api_key = "invalid-key-123"
    
    request = LLMRequest(
        model="claude-3-haiku",
        system_prompt="Test prompt",
        user_message="Test message",
        max_tokens=100,
        temperature=0.7
    )
    
    try:
        await provider.call_model(request)
        print("❌ Expected authentication error but call succeeded")
    except Exception as e:
        print(f"✅ Correctly caught authentication error: {type(e).__name__}")
    
    # Restore original key
    provider.api_key = original_key


async def main():
    """Run all tests"""
    print("🚀 Starting OpenRouter Integration Tests...")
    print("="*50)
    
    try:
        await test_openrouter_provider_direct()
        await test_complete_chat_pipeline()
        await test_error_handling()
        
        print("\n" + "="*50)
        print("🎉 All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())