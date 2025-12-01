#!/usr/bin/env python3
"""
Test script to validate WebSocket chat functionality
Tests connection, message handling, and real-time features
"""
import asyncio
import json
import uuid
import websockets


class WebSocketChatTester:
    """Test WebSocket chat functionality"""

    def __init__(self, base_url: str = "ws://localhost:8000"):
        self.base_url = base_url

    async def test_connection_basic(self):
        """Test basic WebSocket connection"""
        print("🔗 Testing basic WebSocket connection...")

        user_id = f"test_user_{uuid.uuid4().hex[:8]}"
        uri = f"{self.base_url}/api/v1/ws/chat?user_id={user_id}"

        try:
            async with websockets.connect(uri) as websocket:
                print(f"✅ Connected successfully as user: {user_id}")

                # Wait for welcome message
                response = await websocket.recv()
                message = json.loads(response)
                print(f"📨 Received: {message}")

                # Send ping
                await websocket.send(json.dumps({"type": "ping"}))

                # Wait for pong
                response = await websocket.recv()
                pong = json.loads(response)
                print(f"🏓 Ping response: {pong}")

                if pong.get("type") == "pong":
                    print("✅ Ping/pong working correctly")
                else:
                    print("❌ Unexpected ping response")

        except Exception as e:
            print(f"❌ Connection failed: {e}")

    async def test_chat_request(self):
        """Test chat request functionality"""
        print("\n💬 Testing chat request...")

        user_id = f"test_user_{uuid.uuid4().hex[:8]}"
        conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
        uri = f"{self.base_url}/api/v1/ws/chat?user_id={user_id}&conversation_id={conversation_id}"

        try:
            async with websockets.connect(uri) as websocket:
                print("✅ Connected for chat test")

                # Skip welcome message
                await websocket.recv()

                # Send chat request
                chat_message = {
                    "type": "chat_request",
                    "data": {
                        "question": "What is 2+2?",
                        "theme": "academic_help",
                        "context": "Basic math question",
                        "conversation_id": conversation_id,
                    },
                }

                await websocket.send(json.dumps(chat_message))
                print("📤 Sent chat request")

                # Listen for responses
                response_count = 0
                while response_count < 10:  # Limit to prevent infinite loop
                    try:
                        response = await asyncio.wait_for(
                            websocket.recv(), timeout=30.0
                        )
                        message = json.loads(response)

                        print(
                            f"📨 [{message.get('type')}]: {message.get('message', 'No message')}"
                        )

                        # Print detailed response for chat_response
                        if message.get("type") == "chat_response":
                            data = message.get("data", {})
                            print(f"   🤖 Model: {data.get('model_used')}")
                            print(f"   💰 Cost: ${data.get('cost', 0):.6f}")
                            print(f"   ⏱️  Time: {data.get('response_time_ms')}ms")
                            print(f"   📝 Response: {data.get('content', '')[:100]}...")
                            break

                        response_count += 1

                    except asyncio.TimeoutError:
                        print("⏰ Timeout waiting for response")
                        break

                print("✅ Chat request completed")

        except Exception as e:
            print(f"❌ Chat request failed: {e}")

    async def test_user_rating(self):
        """Test user rating functionality"""
        print("\n⭐ Testing user rating...")

        user_id = f"test_user_{uuid.uuid4().hex[:8]}"
        uri = f"{self.base_url}/api/v1/ws/chat?user_id={user_id}"

        try:
            async with websockets.connect(uri) as websocket:
                # Skip welcome message
                await websocket.recv()

                # Send rating
                rating_message = {
                    "type": "user_rating",
                    "data": {
                        "message_id": "test-message-123",
                        "rating": 5,
                        "feedback": "Great response!",
                    },
                }

                await websocket.send(json.dumps(rating_message))
                print("📤 Sent user rating")

                # Wait for response
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                message = json.loads(response)

                if message.get("type") == "rating_submitted":
                    print("✅ Rating submitted successfully")
                else:
                    print(f"❌ Unexpected rating response: {message}")

        except Exception as e:
            print(f"❌ Rating test failed: {e}")

    async def test_multiple_connections(self):
        """Test multiple simultaneous connections"""
        print("\n👥 Testing multiple connections...")

        connections = []
        try:
            # Create 3 connections
            for i in range(3):
                user_id = f"test_user_{i}_{uuid.uuid4().hex[:6]}"
                uri = f"{self.base_url}/api/v1/ws/chat?user_id={user_id}"

                connection = await websockets.connect(uri)
                connections.append((connection, user_id))

                # Skip welcome message
                await connection.recv()
                print(f"✅ Connection {i+1} established for {user_id}")

            # Send messages from each connection
            for i, (connection, user_id) in enumerate(connections):
                message = {
                    "type": "chat_request",
                    "data": {
                        "question": f"Hello from connection {i+1}",
                        "theme": "general_questions",
                        "context": f"Test from user {user_id}",
                    },
                }

                await connection.send(json.dumps(message))
                print(f"📤 Sent message from connection {i+1}")

            # Collect responses
            for i, (connection, user_id) in enumerate(connections):
                try:
                    # Get processing started message
                    response = await asyncio.wait_for(connection.recv(), timeout=5.0)
                    message = json.loads(response)
                    print(f"📨 Connection {i+1} got: {message.get('type')}")
                except asyncio.TimeoutError:
                    print(f"⏰ Connection {i+1} timeout")

            print("✅ Multiple connections test completed")

        except Exception as e:
            print(f"❌ Multiple connections test failed: {e}")
        finally:
            # Clean up connections
            for connection, _ in connections:
                try:
                    await connection.close()
                except Exception:
                    pass

    async def test_admin_endpoint(self):
        """Test admin WebSocket endpoint"""
        print("\n🔧 Testing admin endpoint...")

        uri = f"{self.base_url}/api/v1/ws/admin?admin_token=admin_debug_token"

        try:
            async with websockets.connect(uri) as websocket:
                print("✅ Admin connection established")

                # Skip welcome message
                await websocket.recv()

                # Get stats
                await websocket.send("get_stats")
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                stats = json.loads(response)

                if stats.get("type") == "stats":
                    data = stats.get("data", {})
                    print(f"📊 Total connections: {data.get('total_connections', 0)}")
                    print(f"📊 Unique users: {data.get('unique_users', 0)}")
                    print(
                        f"📊 Active conversations: {data.get('active_conversations', 0)}"
                    )
                    print("✅ Admin stats working")
                else:
                    print(f"❌ Unexpected stats response: {stats}")

        except Exception as e:
            print(f"❌ Admin endpoint test failed: {e}")

    async def run_all_tests(self):
        """Run all WebSocket tests"""
        print("🚀 Starting WebSocket Chat Tests...")
        print("=" * 50)

        # Note: These tests require the backend server to be running
        print("⚠️  Make sure the backend server is running at http://localhost:8000")
        print()

        await self.test_connection_basic()
        await asyncio.sleep(1)

        await self.test_chat_request()
        await asyncio.sleep(1)

        await self.test_user_rating()
        await asyncio.sleep(1)

        await self.test_multiple_connections()
        await asyncio.sleep(1)

        await self.test_admin_endpoint()

        print("\n" + "=" * 50)
        print("🎉 All WebSocket tests completed!")


async def test_http_health():
    """Test WebSocket health endpoint via HTTP"""
    print("🏥 Testing WebSocket health endpoint...")

    import httpx

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/v1/ws/health")

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health endpoint working: {data['status']}")
                print(f"📊 Features: {', '.join(data['features'])}")
            else:
                print(f"❌ Health endpoint returned {response.status_code}")

    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")


async def main():
    """Main test runner"""
    tester = WebSocketChatTester()

    # Test HTTP health first
    await test_http_health()

    # Run WebSocket tests
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
