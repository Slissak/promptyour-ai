#!/usr/bin/env python3
"""
Manual test demonstration for /new command
Simulates a conversation, then uses /new to start fresh
"""
import sys
from terminal_chat import TerminalChat


def test_new_command_demonstration():
    """Demonstrate that /new command properly resets state"""
    print("=" * 70)
    print("DEMONSTRATION: Testing /new command functionality")
    print("=" * 70)
    print()

    # Initialize chat
    chat = TerminalChat(api_base="http://localhost:8001", use_websocket=False)
    print("✓ Created TerminalChat instance")
    print()

    # === PART 1: Simulate first conversation ===
    print("--- PART 1: Simulating First Conversation ---")
    print()

    # Simulate user has sent messages and received responses
    chat.message_history = [
        {"role": "user", "content": "What is Python?", "timestamp": "2024-01-01T10:00:00"},
        {"role": "assistant", "content": "Python is a high-level programming language.", "timestamp": "2024-01-01T10:00:05"},
        {"role": "user", "content": "How do I use loops?", "timestamp": "2024-01-01T10:01:00"},
        {"role": "assistant", "content": "You can use for loops and while loops in Python.", "timestamp": "2024-01-01T10:01:05"}
    ]
    chat.first_message_sent = True
    chat.conversation_theme = "coding_programming"
    chat.conversation_audience = "professionals"
    chat.conversation_response_style = "structured_detailed"
    chat.conversation_context = "Learning Python for data science"
    chat.chosen_model = "claude-3-opus"
    chat.chosen_provider = "anthropic"
    original_conversation_id = chat.conversation_id

    print(f"Conversation ID: {chat.conversation_id}")
    print(f"Message history: {len(chat.message_history)} messages")
    print(f"Theme: {chat.conversation_theme}")
    print(f"Audience: {chat.conversation_audience}")
    print(f"Response Style: {chat.conversation_response_style}")
    print(f"Context: {chat.conversation_context}")
    print(f"Model: {chat.chosen_model}")
    print(f"Provider: {chat.chosen_provider}")
    print(f"First message sent: {chat.first_message_sent}")
    print()

    # Display conversation history
    print("Current conversation history:")
    for i, msg in enumerate(chat.message_history, 1):
        role = msg['role'].upper()
        content = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
        print(f"  {i}. [{role}] {content}")
    print()

    # === PART 2: Execute /new command ===
    print("--- PART 2: Executing /new Command ---")
    print()
    print("Calling: chat.start_new_chat()")
    chat.start_new_chat()
    print()

    # === PART 3: Verify state reset ===
    print("--- PART 3: Verifying State After /new ---")
    print()

    # Check all state variables
    checks = [
        ("Conversation ID changed", chat.conversation_id != original_conversation_id, f"New ID: {chat.conversation_id}"),
        ("Message history cleared", len(chat.message_history) == 0, f"Messages: {len(chat.message_history)}"),
        ("Theme reset", chat.conversation_theme is None, f"Theme: {chat.conversation_theme}"),
        ("Audience reset", chat.conversation_audience is None, f"Audience: {chat.conversation_audience}"),
        ("Response Style reset", chat.conversation_response_style is None, f"Style: {chat.conversation_response_style}"),
        ("Context reset", chat.conversation_context is None, f"Context: {chat.conversation_context}"),
        ("Model reset", chat.chosen_model is None, f"Model: {chat.chosen_model}"),
        ("Provider reset", chat.chosen_provider is None, f"Provider: {chat.chosen_provider}"),
        ("First message flag reset", chat.first_message_sent is False, f"Flag: {chat.first_message_sent}"),
        ("Session messages cleared", len(chat.session_messages) == 0, f"Sessions: {len(chat.session_messages)}")
    ]

    all_passed = True
    for check_name, passed, detail in checks:
        status = "✓" if passed else "✗"
        color = "\033[92m" if passed else "\033[91m"
        reset = "\033[0m"
        print(f"{color}{status}{reset} {check_name:<30} {detail}")
        if not passed:
            all_passed = False

    print()
    print("=" * 70)
    if all_passed:
        print("✓ ALL CHECKS PASSED - /new command works correctly!")
        print("  State is completely reset and ready for a fresh conversation.")
    else:
        print("✗ SOME CHECKS FAILED - /new command has issues!")
        sys.exit(1)
    print("=" * 70)


if __name__ == "__main__":
    test_new_command_demonstration()
