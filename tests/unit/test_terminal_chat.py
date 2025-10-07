"""
Unit tests for terminal_chat.py
Testing the /new command and state reset functionality
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from terminal_chat import TerminalChat


class TestTerminalChatStateReset:
    """Test suite for terminal chat state management and /new command"""

    def test_initial_state(self):
        """Test that TerminalChat initializes with empty state"""
        chat = TerminalChat(api_base="http://localhost:8000")

        assert chat.message_history == []
        assert chat.session_messages == []
        assert chat.first_message_sent == False
        assert chat.conversation_theme is None
        assert chat.conversation_audience is None
        assert chat.conversation_response_style is None
        assert chat.conversation_context is None
        assert chat.chosen_model is None
        assert chat.chosen_provider is None
        assert chat.conversation_id is not None  # Should be generated

    def test_start_new_chat_resets_all_state(self):
        """Test that start_new_chat() resets all conversation state"""
        chat = TerminalChat(api_base="http://localhost:8000")

        # Simulate an active conversation with history
        original_conversation_id = chat.conversation_id
        chat.message_history = [
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "First answer"}
        ]
        chat.session_messages = [{"some": "data"}]
        chat.first_message_sent = True
        chat.conversation_theme = "coding_programming"
        chat.conversation_audience = "professionals"
        chat.conversation_response_style = "structured_detailed"
        chat.conversation_context = "Working on Python project"
        chat.chosen_model = "claude-3-opus"
        chat.chosen_provider = "anthropic"

        # Call start_new_chat
        chat.start_new_chat()

        # Verify all state is reset
        assert chat.message_history == [], "message_history should be empty"
        assert chat.session_messages == [], "session_messages should be empty"
        assert chat.first_message_sent == False, "first_message_sent should be False"
        assert chat.conversation_theme is None, "conversation_theme should be None"
        assert chat.conversation_audience is None, "conversation_audience should be None"
        assert chat.conversation_response_style is None, "conversation_response_style should be None"
        assert chat.conversation_context is None, "conversation_context should be None"
        assert chat.chosen_model is None, "chosen_model should be None"
        assert chat.chosen_provider is None, "chosen_provider should be None"
        assert chat.conversation_id != original_conversation_id, "conversation_id should be different"

    def test_start_new_chat_generates_new_conversation_id(self):
        """Test that start_new_chat() generates a unique conversation ID"""
        chat = TerminalChat(api_base="http://localhost:8000")

        conversation_ids = set()

        # Generate multiple conversation IDs
        for _ in range(5):
            conversation_ids.add(chat.conversation_id)
            chat.start_new_chat()

        # All IDs should be unique
        assert len(conversation_ids) == 5, "All conversation IDs should be unique"

        # IDs should follow expected format
        for conv_id in conversation_ids:
            assert conv_id.startswith("conv_"), "Conversation ID should start with 'conv_'"
            assert len(conv_id) == 13, "Conversation ID should be 'conv_' + 8 hex chars"

    def test_message_history_isolation_between_sessions(self):
        """Test that message history doesn't leak between new chat sessions"""
        chat = TerminalChat(api_base="http://localhost:8000")

        # First conversation
        chat.message_history = [
            {"role": "user", "content": "Question 1"},
            {"role": "assistant", "content": "Answer 1"},
            {"role": "user", "content": "Question 2"},
            {"role": "assistant", "content": "Answer 2"}
        ]

        first_session_history = chat.message_history.copy()
        assert len(first_session_history) == 4

        # Start new chat
        chat.start_new_chat()

        # Add new messages to second conversation
        chat.message_history = [
            {"role": "user", "content": "New question"},
            {"role": "assistant", "content": "New answer"}
        ]

        second_session_history = chat.message_history.copy()
        assert len(second_session_history) == 2

        # Verify first session history hasn't changed
        assert len(first_session_history) == 4
        assert first_session_history != second_session_history

    def test_conversation_settings_reset(self):
        """Test that all conversation settings are properly reset"""
        chat = TerminalChat(api_base="http://localhost:8000")

        # Set all possible conversation settings
        chat.conversation_theme = "academic_help"
        chat.conversation_audience = "university_level"
        chat.conversation_response_style = "comprehensive"
        chat.conversation_context = "Studying for finals"
        chat.chosen_model = "gpt-4"
        chat.chosen_provider = "openai"

        # Verify settings are set
        assert chat.conversation_theme == "academic_help"
        assert chat.conversation_audience == "university_level"
        assert chat.conversation_response_style == "comprehensive"
        assert chat.conversation_context == "Studying for finals"
        assert chat.chosen_model == "gpt-4"
        assert chat.chosen_provider == "openai"

        # Start new chat
        chat.start_new_chat()

        # Verify all settings are None
        assert chat.conversation_theme is None
        assert chat.conversation_audience is None
        assert chat.conversation_response_style is None
        assert chat.conversation_context is None
        assert chat.chosen_model is None
        assert chat.chosen_provider is None


class TestTerminalChatConfiguration:
    """Test terminal chat configuration and initialization"""

    def test_available_themes_list(self):
        """Test that all required themes are available"""
        chat = TerminalChat()

        expected_themes = [
            "academic_help",
            "creative_writing",
            "coding_programming",
            "business_professional",
            "personal_learning",
            "research_analysis",
            "problem_solving",
            "tutoring_education",
            "general_questions"
        ]

        assert chat.themes == expected_themes

    def test_available_audiences_list(self):
        """Test that all required audiences are available"""
        chat = TerminalChat()

        expected_audiences = [
            "small_kids",
            "teenagers",
            "adults",
            "university_level",
            "professionals",
            "seniors"
        ]

        assert chat.audiences == expected_audiences

    def test_available_response_styles_list(self):
        """Test that all required response styles are available"""
        chat = TerminalChat()

        expected_styles = [
            "paragraph_brief",
            "structured_detailed",
            "instructions_only",
            "comprehensive"
        ]

        assert chat.response_styles == expected_styles


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
