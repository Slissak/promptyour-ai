#!/usr/bin/env python3
"""
Test script to validate LM Studio integration and unified LLM provider
Tests local LLM functionality, provider routing, and fallback mechanisms
"""
import asyncio
import json
import httpx
from typing import Dict, Any


class LMStudioIntegrationTester:
    """Test LM Studio and unified LLM provider functionality"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.lm_studio_url = "http://localhost:1234/v1"
    
    async def test_lm_studio_direct(self):
        """Test direct LM Studio API connection"""
        print("🔗 Testing direct LM Studio connection...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test LM Studio health
                response = await client.get(f"{self.lm_studio_url}/models")
                
                if response.status_code == 200:
                    models = response.json()
                    print(f"✅ LM Studio is running!")
                    print(f"   Available models: {len(models.get('data', []))}")
                    
                    for model in models.get('data', [])[:3]:  # Show first 3 models
                        print(f"   - {model.get('id', 'unknown')}")
                    
                    return True
                else:
                    print(f"❌ LM Studio returned HTTP {response.status_code}")
                    return False
                    
        except httpx.ConnectError:
            print("❌ LM Studio is not running")
            print("   💡 To test with LM Studio:")
            print("   1. Download from https://lmstudio.ai/")
            print("   2. Load a model (e.g., Llama 3.2 3B)")
            print("   3. Start the local server")
            return False
        except Exception as e:
            print(f"❌ Error connecting to LM Studio: {e}")
            return False

    async def test_provider_status_api(self):
        """Test the provider status API endpoints"""
        print("\n📊 Testing provider status API...")
        
        endpoints = [
            "/api/v1/providers/status",
            "/api/v1/providers/health", 
            "/api/v1/providers/lm-studio/status",
            "/api/v1/providers/openrouter/status"
        ]
        
        async with httpx.AsyncClient() as client:
            for endpoint in endpoints:
                try:
                    response = await client.get(f"{self.api_base_url}{endpoint}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"✅ {endpoint}: {data.get('success', 'OK')}")
                        
                        # Show key info for status endpoints
                        if "status" in endpoint:
                            if "data" in data:
                                status_data = data["data"]
                                if "providers" in status_data:
                                    for provider, info in status_data["providers"].items():
                                        print(f"   📡 {provider}: {info.get('status', 'unknown')}")
                    else:
                        print(f"❌ {endpoint}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ {endpoint}: {e}")

    async def test_unified_provider_routing(self):
        """Test the unified provider's routing logic"""
        print("\n🔀 Testing provider routing...")
        
        try:
            async with httpx.AsyncClient() as client:
                # Test provider health check
                response = await client.get(f"{self.api_base_url}/api/v1/providers/health")
                
                if response.status_code == 200:
                    health_data = response.json()["data"]
                    print(f"✅ Unified provider status: {health_data['status']}")
                    print(f"   Active providers: {', '.join(health_data['active_providers'])}")
                    print(f"   Preferred: {health_data.get('preferred_provider', 'auto')}")
                    print(f"   Prefer local: {health_data.get('prefer_local_models', True)}")
                else:
                    print(f"❌ Health check failed: HTTP {response.status_code}")
                    
        except Exception as e:
            print(f"❌ Error testing routing: {e}")

    async def test_model_listing(self):
        """Test model listing from all providers"""
        print("\n📋 Testing model listing...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_base_url}/api/v1/providers/models")
                
                if response.status_code == 200:
                    models_data = response.json()["data"]
                    
                    for provider, info in models_data.items():
                        status = info.get("status", "unknown")
                        count = info.get("count", 0)
                        print(f"✅ {provider}: {status} ({count} models)")
                        
                        if provider == "lm_studio" and info.get("loaded_model"):
                            print(f"   🔥 Loaded: {info['loaded_model']}")
                            
                else:
                    print(f"❌ Model listing failed: HTTP {response.status_code}")
                    
        except Exception as e:
            print(f"❌ Error listing models: {e}")

    async def test_setup_guide(self):
        """Test the setup guide endpoint"""
        print("\n📖 Testing setup guide...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_base_url}/api/v1/providers/setup-guide")
                
                if response.status_code == 200:
                    guide_data = response.json()["data"]
                    recommendations = guide_data.get("recommendations", [])
                    
                    print(f"✅ Setup guide generated ({len(recommendations)} recommendations)")
                    
                    for rec in recommendations:
                        priority = rec.get("priority", "unknown")
                        title = rec.get("title", "No title")
                        print(f"   {priority.upper()}: {title}")
                        
                else:
                    print(f"❌ Setup guide failed: HTTP {response.status_code}")
                    
        except Exception as e:
            print(f"❌ Error getting setup guide: {e}")

    async def test_provider_integration(self):
        """Test the actual LLM provider integration"""
        print("\n🧪 Testing provider integration...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{self.api_base_url}/api/v1/providers/test")
                
                if response.status_code == 200:
                    test_data = response.json()
                    
                    if test_data.get("success"):
                        data = test_data["data"]
                        print("✅ Provider integration test successful!")
                        print(f"   Provider used: {data.get('provider_used')}")
                        print(f"   Model used: {data.get('model_used')}")
                        print(f"   Response: {data.get('response_content', '')[:100]}...")
                        print(f"   Tokens used: {data.get('tokens_used')}")
                        print(f"   Cost: ${data.get('cost', 0):.6f}")
                        print(f"   Response time: {data.get('response_time_ms')}ms")
                    else:
                        print("❌ Provider integration test failed")
                        error = test_data.get("error", "Unknown error")
                        print(f"   Error: {error}")
                        
                        recommendations = test_data.get("recommendations", [])
                        if recommendations:
                            print("   💡 Recommendations:")
                            for rec in recommendations:
                                print(f"   - {rec}")
                else:
                    print(f"❌ Integration test failed: HTTP {response.status_code}")
                    
        except Exception as e:
            print(f"❌ Error testing integration: {e}")

    async def test_troubleshooting(self):
        """Test the troubleshooting endpoint"""
        print("\n🔧 Testing troubleshooting diagnostics...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_base_url}/api/v1/providers/troubleshoot")
                
                if response.status_code == 200:
                    diag_data = response.json()["data"]
                    checks = diag_data.get("checks", [])
                    
                    print(f"✅ Diagnostics completed ({len(checks)} checks)")
                    
                    for check in checks:
                        name = check.get("name", "Unknown")
                        status = check.get("status", "unknown")
                        print(f"   {status.upper()}: {name}")
                        
                        if status != "healthy":
                            suggestions = check.get("suggestions", [])
                            if suggestions:
                                print(f"     💡 {suggestions[0]}")
                else:
                    print(f"❌ Troubleshooting failed: HTTP {response.status_code}")
                    
        except Exception as e:
            print(f"❌ Error running diagnostics: {e}")

    async def test_chat_with_local_llm(self):
        """Test a full chat request using the unified provider"""
        print("\n💬 Testing full chat flow with unified provider...")
        
        chat_request = {
            "question": "What is 2+2? Please explain briefly.",
            "theme": "academic_help",
            "context": "Simple math question for testing local LLM"
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.api_base_url}/api/v1/chat/process",
                    json=chat_request
                )
                
                if response.status_code == 200:
                    chat_data = response.json()
                    
                    if chat_data.get("success"):
                        data = chat_data["data"]
                        print("✅ Full chat flow successful!")
                        print(f"   Model used: {data.get('model_used')}")
                        print(f"   Provider: {data.get('provider')}")
                        print(f"   Response: {data.get('content', '')[:150]}...")
                        print(f"   Cost: ${data.get('cost', 0):.6f}")
                        print(f"   Reasoning: {data.get('reasoning', 'N/A')}")
                    else:
                        print("❌ Chat flow failed")
                        print(f"   Error: {chat_data.get('error', 'Unknown error')}")
                else:
                    print(f"❌ Chat request failed: HTTP {response.status_code}")
                    try:
                        error_data = response.json()
                        print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                    except:
                        pass
                    
        except Exception as e:
            print(f"❌ Error testing chat flow: {e}")

    async def run_all_tests(self):
        """Run comprehensive LM Studio integration tests"""
        print("🚀 Starting LM Studio Integration Tests...")
        print("="*60)
        
        # Test 1: Direct LM Studio connection
        lm_studio_available = await self.test_lm_studio_direct()
        
        # Test 2: API endpoints
        await self.test_provider_status_api()
        
        # Test 3: Provider routing
        await self.test_unified_provider_routing()
        
        # Test 4: Model listing
        await self.test_model_listing()
        
        # Test 5: Setup guide
        await self.test_setup_guide()
        
        # Test 6: Provider integration test
        await self.test_provider_integration()
        
        # Test 7: Troubleshooting
        await self.test_troubleshooting()
        
        # Test 8: Full chat flow (if any provider is available)
        await self.test_chat_with_local_llm()
        
        print("\n" + "="*60)
        print("🎉 LM Studio Integration Tests Completed!")
        
        if lm_studio_available:
            print("\n✅ LM Studio is properly integrated and working!")
        else:
            print("\n⚠️  LM Studio is not running, but OpenRouter fallback should work")
            print("   For the full local LLM experience:")
            print("   1. Install LM Studio from https://lmstudio.ai/")
            print("   2. Download and load a model (recommend Llama 3.2 3B)")
            print("   3. Start the local server")
            print("   4. Re-run this test")


async def main():
    """Main test runner"""
    print("⚠️  Make sure the backend server is running at http://localhost:8000\n")
    
    tester = LMStudioIntegrationTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())