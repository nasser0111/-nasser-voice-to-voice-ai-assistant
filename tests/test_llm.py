"""Unit tests for Cohere response handling without network calls."""

import unittest
from types import SimpleNamespace

from voice_assistant.llm import CohereChatModel


class FakeCohereClient:
    def __init__(self) -> None:
        self.requests = []

    def chat(self, **kwargs):
        self.requests.append(kwargs)
        return SimpleNamespace(
            message=SimpleNamespace(
                content=[SimpleNamespace(type="text", text="Test answer")]
            )
        )


class CohereChatModelTests(unittest.TestCase):
    def test_generate_extracts_text_and_keeps_history(self) -> None:
        client = FakeCohereClient()
        model = CohereChatModel(
            api_key="test-key",
            model="test-model",
            system_prompt="Be helpful.",
            client=client,
        )

        first = model.generate("First question")
        second = model.generate("Second question")

        self.assertEqual(first, "Test answer")
        self.assertEqual(second, "Test answer")
        self.assertEqual(client.requests[0]["messages"][0]["role"], "system")
        second_messages = client.requests[1]["messages"]
        self.assertTrue(
            any(item["content"] == "First question" for item in second_messages)
        )

    def test_extract_text_accepts_dictionary_responses(self) -> None:
        response = {"message": {"content": [{"text": "Dictionary answer"}]}}
        self.assertEqual(
            CohereChatModel._extract_text(response), "Dictionary answer"
        )


if __name__ == "__main__":
    unittest.main()

