"""Text-to-speech and audio playback providers."""

from __future__ import annotations

from pathlib import Path

from .errors import AudioPlaybackError, ConfigurationError, ExternalServiceError


class GoogleTextToSpeech:
    """Convert text to an MP3 file using gTTS."""

    def __init__(self, language: str = "en") -> None:
        self.language = language

    def synthesize(self, text: str, output_path: Path) -> Path:
        cleaned = text.strip()
        if not cleaned:
            raise ValueError("Text-to-speech input cannot be empty")

        try:
            from gtts import gTTS
            from gtts.tts import gTTSError
        except ImportError as error:
            raise ConfigurationError(
                "gTTS is not installed. Run: "
                "python -m pip install -r requirements.txt"
            ) from error

        output_path = output_path.expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            gTTS(text=cleaned, lang=self.language, slow=False).save(
                str(output_path)
            )
        except (gTTSError, OSError, ValueError) as error:
            raise ExternalServiceError(
                f"Text-to-speech generation failed: {error}"
            ) from error
        return output_path


class PlaysoundAudioPlayer:
    """Play an audio file with playsound3."""

    def play(self, audio_path: Path) -> None:
        if not audio_path.is_file():
            raise AudioPlaybackError(f"Audio file was not found: {audio_path}")
        try:
            from playsound3 import playsound
        except ImportError as error:
            raise ConfigurationError(
                "playsound3 is not installed. Run: "
                "python -m pip install -r requirements.txt"
            ) from error
        try:
            playsound(str(audio_path))
        except Exception as error:
            raise AudioPlaybackError(
                f"The MP3 was created but could not be played: {error}"
            ) from error

