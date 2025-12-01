
import json

import pytest
from httpx import AsyncClient

from backend.app.main import app

# Define test cases for different languages
language_tests = [
    {
        "language": "Hebrew",
        "question": "מה столица של צרפת?",
        "expected_answer": ["פריז", "פרז"],
    },
    {
        "language": "Arabic",
        "question": "ما هي عاصمة فرنسا؟",
        "expected_answer": ["باريس"],
    },
    {
        "language": "Russian",
        "question": "Какая столица Франции?",
        "expected_answer": ["Париж"],
    },
    {
        "language": "Chinese",
        "question": "法国的首都是哪里？",
        "expected_answer": ["巴黎"],
    },
    {
        "language": "Hindi",
        "question": "फ्रांस की राजधानी क्या है?",
        "expected_answer": ["पेरिस", "पारिस"],
    },
]

@pytest.mark.skip(reason="Quick chat model is not powerful enough for multilingual tests")
@pytest.mark.asyncio
@pytest.mark.parametrize("lang_test", language_tests)
async def test_quick_chat_multilingual(lang_test):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/chat/quick",
            json={"question": lang_test["question"]},
        )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["content"] is not None
        assert any(variation in response_data["content"] for variation in lang_test["expected_answer"])

@pytest.mark.asyncio
@pytest.mark.parametrize("lang_test", language_tests)
async def test_enhanced_chat_multilingual(lang_test):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/chat/message",
            json={
                "question": lang_test["question"],
                "theme": "general_questions",
                "audience": "adults",
            },
        )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["content"] is not None
        assert any(variation in response_data["content"] for variation in lang_test["expected_answer"])
