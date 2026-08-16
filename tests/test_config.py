"""Unit tests for configuration validation."""

import unittest

from voice_assistant.config import AppConfig
from voice_assistant.errors import ConfigurationError


class AppConfigTests(unittest.TestCase):
    def test_valid_configuration(self) -> None:
        config = AppConfig.from_environment(
            {
                "COHERE_API_KEY": "test-key",
                "COHERE_MODEL": "command-test",
                "SPEECH_LANGUAGE": "ar-SA",
                "TTS_LANGUAGE": "ar",
                "ASSISTANT_LANGUAGE": "Arabic",
                "MICROPHONE_INDEX": "2",
                "LISTEN_TIMEOUT": "6",
                "PHRASE_TIME_LIMIT": "15",
            }
        )

        self.assertEqual(config.cohere_model, "command-test")
        self.assertEqual(config.microphone_index, 2)
        self.assertIn("Arabic", config.system_prompt)

    def test_missing_api_key_is_rejected(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "COHERE_API_KEY"):
            AppConfig.from_environment({})

    def test_invalid_timeout_is_rejected(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "LISTEN_TIMEOUT"):
            AppConfig.from_environment(
                {"COHERE_API_KEY": "key", "LISTEN_TIMEOUT": "never"}
            )


if __name__ == "__main__":
    unittest.main()

