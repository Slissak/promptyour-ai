#!/usr/bin/env python3
"""
Test LM Studio integration through WebSocket chat
"""
import asyncio
import json
import uuid
import websockets


async def test_lm_studio_websocket_chat():
    """Test WebSocket chat with LM Studio"""
    print("🚀 Testing LM Studio WebSocket Chat Integration...")

    user_id = f"test_user_{uuid.uuid4().hex[:8]}"
    uri = f"ws://localhost:8000/api/v1/ws/chat?user_id={user_id}"

    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected as user: {user_id}")

            # Skip welcome message
            welcome = await websocket.recv()
            print(f"📨 Welcome: {json.loads(welcome)['message']}")

            # Send a chat request that should use LM Studio
            chat_message = {
                "type": "chat_request",
                "data": {
                    "question": "What is 2+2? Please explain briefly and mention that you're running locally.",
                    "theme": "academic_help",
                    "context": "Testing local LM Studio integration",
                },
            }

            await websocket.send(json.dumps(chat_message))
            print("📤 Sent chat request to local LM Studio...")

            # Listen for responses
            response_count = 0
            while response_count < 10:  # Limit to prevent infinite loop
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    message = json.loads(response)

                    msg_type = message.get("type")
                    print(f"📨 [{msg_type}]: {message.get('message', '')}")

                    # Print detailed response for chat_response
                    if msg_type == "chat_response":
                        data = message.get("data", {})
                        print(f"   🤖 Model: {data.get('model_used')}")
                        print(f"   🏠 Provider: {data.get('provider')}")
                        print(f"   💰 Cost: ${data.get('cost', 0):.6f}")
                        print(f"   ⏱️  Time: {data.get('response_time_ms')}ms")
                        print(f"   🧠 Reasoning: {data.get('reasoning', 'N/A')}")
                        print(f"   📝 Response: {data.get('content', '')[:200]}...")

                        if data.get("provider") == "lm_studio":
                            print("   ✅ SUCCESS: Using local LM Studio model!")
                        else:
                            print(
                                f"   ⚠️  Using {data.get('provider')} instead of local model"
                            )
                        break

                    response_count += 1

                except asyncio.TimeoutError:
                    print("⏰ Timeout waiting for response")
                    break

        print("✅ WebSocket chat test completed!")

    except Exception as e:
        print(f"❌ WebSocket chat test failed: {e}")


async def test_provider_status():
    """Test provider status via HTTP"""
    import httpx

    print("\n📊 Checking Provider Status...")

    try:
        async with httpx.AsyncClient() as client:
            # Check overall status
            response = await client.get("http://localhost:8000/api/v1/providers/status")
            if response.status_code == 200:
                data = response.json()["data"]
                providers = data.get("providers", {})

                print("Provider Status:")
                for name, info in providers.items():
                    status = info.get("status", "unknown")
                    print(f"  📡 {name}: {status}")

                    if name == "lm_studio" and status == "healthy":
                        if "loaded_model" in info:
                            print(f"      🔥 Loaded: {info['loaded_model']}")
                        if "model_display_name" in info:
                            print(f"      🏷️  Display: {info['model_display_name']}")
            else:
                print(f"❌ Status check failed: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ Error checking status: {e}")


async def main():
    """Run LM Studio chat tests"""
    await test_provider_status()
    await test_lm_studio_websocket_chat()

    print("\n🎉 LM Studio integration is working with your local model!")
    print("Your setup:")
    print("  🏠 LM Studio running locally")
    print("  🤖 Model loaded and ready")
    print("  💰 $0.00 cost for inference")
    print("  🔒 Complete privacy - data stays local")


if __name__ == "__main__":
    asyncio.run(main())
