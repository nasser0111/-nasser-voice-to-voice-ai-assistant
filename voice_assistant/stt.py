"""Speech-to-text provider based on the SpeechRecognition package."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .errors import ConfigurationError, ExternalServiceError, SpeechInputError


class GoogleSpeechToText:
    """Capture audio and transcribe it with Google Speech Recognition."""

    def __init__(
        self,
        language: str = "en-US",
        microphone_index: int | None = None,
        listen_timeout: float = 8.0,
        phrase_time_limit: float = 20.0,
        recognizer: Any | None = None,
        speech_module: Any | None = None,
    ) -> None:
        if speech_module is None:
            try:
                import speech_recognition as speech_module
            except ImportError as error:
                raise ConfigurationError(
                    "SpeechRecognition is not installed. Run: "
                    "python -m pip install -r requirements.txt"
                ) from error

        self._speech = speech_module
        self._recognizer = recognizer or speech_module.Recognizer()
        self.language = language
        self.microphone_index = microphone_index
        self.listen_timeout = listen_timeout
        self.phrase_time_limit = phrase_time_limit

    @classmethod
    def list_microphones(cls) -> list[str]:
        try:
            import speech_recognition as sr
        except ImportError as error:
            raise ConfigurationError(
                "SpeechRecognition is not installed."
            ) from error
        try:
            return list(sr.Microphone.list_microphone_names())
        except (AttributeError, OSError) as error:
            raise ConfigurationError(
                "Microphone access requires PyAudio and a working audio device."
            ) from error

    def transcribe_microphone(self) -> str:
        print("Listening... speak after the microphone is calibrated.")
        try:
            with self._speech.Microphone(
                device_index=self.microphone_index
            ) as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.8)
                audio = self._recognizer.listen(
                    source,
                    timeout=self.listen_timeout,
                    phrase_time_limit=self.phrase_time_limit,
                )
        except self._speech.WaitTimeoutError as error:
            raise SpeechInputError(
                "No speech was detected before the listening timeout."
            ) from error
        except (AttributeError, OSError) as error:
            raise SpeechInputError(
                "The microphone could not be opened. Check permissions, PyAudio, "
                "and MICROPHONE_INDEX."
            ) from error

        return self._recognize(audio)

    def transcribe_file(self, audio_path: Path) -> str:
        if not audio_path.is_file():
            raise SpeechInputError(f"Audio file was not found: {audio_path}")

        try:
            with self._speech.AudioFile(str(audio_path)) as source:
                audio = self._recognizer.record(source)
        except (ValueError, OSError) as error:
            raise SpeechInputError(
                "The audio file must be a supported PCM WAV, AIFF, or FLAC file."
            ) from error

        return self._recognize(audio)

    def _recognize(self, audio: Any) -> str:
        try:
            text = self._recognizer.recognize_google(
                audio, language=self.language
            )
        except self._speech.UnknownValueError as error:
            raise SpeechInputError(
                "Speech was captured, but the words could not be understood."
            ) from error
        except self._speech.RequestError as error:
            raise ExternalServiceError(
                f"Speech-to-text service request failed: {error}"
            ) from error

        cleaned = str(text).strip()
        if not cleaned:
            raise SpeechInputError("Speech-to-text returned an empty result.")
        return cleaned

