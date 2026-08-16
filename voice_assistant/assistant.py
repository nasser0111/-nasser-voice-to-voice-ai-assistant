"""Provider-independent voice assistant pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class SpeechProvider(Protocol):
    def transcribe_microphone(self) -> str: ...

    def transcribe_file(self, audio_path: Path) -> str: ...


class LanguageModel(Protocol):
    def generate(self, user_text: str) -> str: ...


class SpeechSynthesizer(Protocol):
    def synthesize(self, text: str, output_path: Path) -> Path: ...


class AudioPlayer(Protocol):
    def play(self, audio_path: Path) -> None: ...


@dataclass(frozen=True)
class TurnResult:
    """Complete result for one voice-assistant turn."""

    user_text: str
    assistant_text: str
    audio_path: Path


class VoiceAssistant:
    """Orchestrate STT, LLM generation, TTS, and optional playback."""

    def __init__(
        self,
        language_model: LanguageModel,
        speech_synthesizer: SpeechSynthesizer,
        speech_provider: SpeechProvider | None = None,
        audio_player: AudioPlayer | None = None,
    ) -> None:
        self.language_model = language_model
        self.speech_synthesizer = speech_synthesizer
        self.speech_provider = speech_provider
        self.audio_player = audio_player

    def run_microphone(self, output_path: Path, play_audio: bool = True) -> TurnResult:
        if self.speech_provider is None:
            raise RuntimeError("A speech provider is required for microphone mode")
        user_text = self.speech_provider.transcribe_microphone()
        return self.process_text(user_text, output_path, play_audio)

    def run_audio_file(
        self,
        input_path: Path,
        output_path: Path,
        play_audio: bool = True,
    ) -> TurnResult:
        if self.speech_provider is None:
            raise RuntimeError("A speech provider is required for audio-file mode")
        user_text = self.speech_provider.transcribe_file(input_path)
        return self.process_text(user_text, output_path, play_audio)

    def process_text(
        self,
        user_text: str,
        output_path: Path,
        play_audio: bool = True,
    ) -> TurnResult:
        cleaned = user_text.strip()
        if not cleaned:
            raise ValueError("User text cannot be empty")

        assistant_text = self.language_model.generate(cleaned).strip()
        if not assistant_text:
            raise ValueError("The language model returned an empty response")

        audio_path = self.speech_synthesizer.synthesize(
            assistant_text, output_path
        )
        if play_audio and self.audio_player is not None:
            self.audio_player.play(audio_path)

        return TurnResult(
            user_text=cleaned,
            assistant_text=assistant_text,
            audio_path=audio_path,
        )

