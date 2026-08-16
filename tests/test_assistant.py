"""Unit tests for the provider-independent assistant pipeline."""

import tempfile
import unittest
from pathlib import Path

from voice_assistant.assistant import VoiceAssistant


class FakeSpeechProvider:
    def transcribe_microphone(self) -> str:
        return "What is computer vision?"

    def transcribe_file(self, audio_path: Path) -> str:
        return f"Transcribed from {audio_path.name}"


class FakeLanguageModel:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate(self, user_text: str) -> str:
        self.prompts.append(user_text)
        return "Computer vision helps computers understand images."


class FakeSynthesizer:
    def __init__(self) -> None:
        self.inputs: list[str] = []

    def synthesize(self, text: str, output_path: Path) -> Path:
        self.inputs.append(text)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"fake-mp3")
        return output_path


class FakePlayer:
    def __init__(self) -> None:
        self.played: list[Path] = []

    def play(self, audio_path: Path) -> None:
        self.played.append(audio_path)


class VoiceAssistantTests(unittest.TestCase):
    def setUp(self) -> None:
        self.llm = FakeLanguageModel()
        self.tts = FakeSynthesizer()
        self.player = FakePlayer()
        self.assistant = VoiceAssistant(
            language_model=self.llm,
            speech_synthesizer=self.tts,
            speech_provider=FakeSpeechProvider(),
            audio_player=self.player,
        )

    def test_complete_microphone_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "answer.mp3"
            result = self.assistant.run_microphone(output)

            self.assertEqual(result.user_text, "What is computer vision?")
            self.assertTrue(result.audio_path.is_file())
            self.assertEqual(self.llm.prompts, [result.user_text])
            self.assertEqual(self.player.played, [output])

    def test_audio_file_pipeline_without_playback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "answer.mp3"
            result = self.assistant.run_audio_file(
                Path("question.wav"), output, play_audio=False
            )

            self.assertEqual(result.user_text, "Transcribed from question.wav")
            self.assertEqual(self.player.played, [])

    def test_text_mode_rejects_empty_input(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot be empty"):
            self.assistant.process_text("   ", Path("answer.mp3"))


if __name__ == "__main__":
    unittest.main()

