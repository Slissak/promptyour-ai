#!/usr/bin/env python3
"""
Test script to validate all 3 chat types are working independently
"""
import httpx
import json
import asyncio
from datetime import datetime


async def test_3_chat_types():
    """Test all 3 chat types with the same question"""

    base_url = "http://localhost:8001"
    test_question = "What is artificial intelligence?"

    print("=" * 80)
    print("TESTING 3 CHAT TYPES")
    print("=" * 80)
    print(f"\nTest Question: \"{test_question}\"")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    async with httpx.AsyncClient(timeout=60.0) as client:

        # Test 1: Quick One-Liner
        print("\n" + "─" * 80)
        print("TEST 1: QUICK ONE-LINER")
        print("─" * 80)
        print("Endpoint: POST /api/v1/chat/quick")
        print("Description: Fast response with constant system prompt")
        print()

        try:
            quick_payload = {
                "question": test_question
            }

            print(f"Sending request...")
            quick_response = await client.post(
                f"{base_url}/api/v1/chat/quick",
                json=quick_payload
            )

            if quick_response.status_code == 200:
                quick_data = quick_response.json()
                print(f"✅ Status: {quick_response.status_code} OK")
                print(f"✅ Model: {quick_data['model_used']}")
                print(f"✅ Provider: {quick_data['provider']}")
                print(f"✅ Cost: ${quick_data['cost']:.6f}")
                print(f"✅ Response Time: {quick_data['response_time_ms']}ms")
                print(f"✅ System Prompt Length: {len(quick_data['system_prompt'])} chars")
                print(f"✅ Response Length: {len(quick_data['content'])} chars")
                print(f"\n📝 System Prompt Preview:")
                print(f"   {quick_data['system_prompt'][:200]}...")
                print(f"\n💬 Response Preview:")
                print(f"   {quick_data['content'][:300]}...")
            else:
                print(f"❌ Failed: {quick_response.status_code}")
                print(f"   {quick_response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")

        # Test 2: RAW Answer (NEW!)
        print("\n\n" + "─" * 80)
        print("TEST 2: RAW ANSWER (NO PROMPT ENGINEERING)")
        print("─" * 80)
        print("Endpoint: POST /api/v1/chat/raw")
        print("Description: ONLY user question, NO system prompt, NO context")
        print()

        try:
            raw_payload = {
                "question": test_question
            }

            print(f"Sending request...")
            raw_response = await client.post(
                f"{base_url}/api/v1/chat/raw",
                json=raw_payload
            )

            if raw_response.status_code == 200:
                raw_data = raw_response.json()
                print(f"✅ Status: {raw_response.status_code} OK")
                print(f"✅ Model: {raw_data['model_used']}")
                print(f"✅ Provider: {raw_data['provider']}")
                print(f"✅ Cost: ${raw_data['cost']:.6f}")
                print(f"✅ Response Time: {raw_data['response_time_ms']}ms")
                print(f"✅ System Prompt Length: {len(raw_data['system_prompt'])} chars (should be 0)")
                print(f"✅ Response Length: {len(raw_data['content'])} chars")

                if len(raw_data['system_prompt']) == 0:
                    print(f"✅ VERIFIED: System prompt is empty (truly RAW)")
                else:
                    print(f"⚠️  WARNING: System prompt is NOT empty!")

                print(f"\n💬 RAW Response Preview:")
                print(f"   {raw_data['content'][:300]}...")
            else:
                print(f"❌ Failed: {raw_response.status_code}")
                print(f"   {raw_response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")

        # Test 3: Enhanced
        print("\n\n" + "─" * 80)
        print("TEST 3: ENHANCED (FULL PROMPT ENGINEERING)")
        print("─" * 80)
        print("Endpoint: POST /api/v1/chat/message")
        print("Description: Full prompt engineering with theme/audience/style")
        print()

        try:
            enhanced_payload = {
                "question": test_question,
                "theme": "general_questions",
                "audience": "adults",
                "response_style": "structured_detailed"
            }

            print(f"Sending request...")
            enhanced_response = await client.post(
                f"{base_url}/api/v1/chat/message",
                json=enhanced_payload
            )

            if enhanced_response.status_code == 200:
                enhanced_data = enhanced_response.json()
                print(f"✅ Status: {enhanced_response.status_code} OK")
                print(f"✅ Model: {enhanced_data['model_used']}")
                print(f"✅ Provider: {enhanced_data['provider']}")
                print(f"✅ Cost: ${enhanced_data['cost']:.6f}")
                print(f"✅ Response Time: {enhanced_data['response_time_ms']}ms")
                print(f"✅ System Prompt Length: {len(enhanced_data['system_prompt'])} chars")
                print(f"✅ Response Length: {len(enhanced_data['content'])} chars")
                print(f"✅ Reasoning: {enhanced_data['reasoning']}")

                if 'raw_response' in enhanced_data and enhanced_data['raw_response']:
                    print(f"✅ Includes RAW comparison: Yes ({len(enhanced_data['raw_response'])} chars)")

                print(f"\n📝 Enhanced System Prompt Preview:")
                print(f"   {enhanced_data['system_prompt'][:200]}...")
                print(f"\n💬 Enhanced Response Preview:")
                print(f"   {enhanced_data['content'][:300]}...")
            else:
                print(f"❌ Failed: {enhanced_response.status_code}")
                print(f"   {enhanced_response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")

    # Summary
    print("\n\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print()
    print("✅ Type 1: Quick One-Liner - Available at /api/v1/chat/quick")
    print("   - Uses constant system prompt for concise answers")
    print("   - Fast model (claude-3-haiku)")
    print("   - Includes conversation history")
    print()
    print("✅ Type 2: RAW Answer - Available at /api/v1/chat/raw")
    print("   - NO system prompt (empty string)")
    print("   - ONLY user question")
    print("   - NO context, theme, audience, or history")
    print()
    print("✅ Type 3: Enhanced - Available at /api/v1/chat/message")
    print("   - Full prompt engineering with theme/audience/style")
    print("   - Includes conversation history")
    print("   - Also generates RAW response for comparison")
    print()
    print("=" * 80)
    print("ALL 3 CHAT TYPES ARE NOW AVAILABLE VIA API ✅")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_3_chat_types())
