"""Environment-based application configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .errors import ConfigurationError


def _read_float(values: Mapping[str, str], name: str, default: float) -> float:
    raw_value = values.get(name, "").strip()
    if not raw_value:
        return default
    try:
        value = float(raw_value)
    except ValueError as error:
        raise ConfigurationError(f"{name} must be a number") from error
    if value <= 0:
        raise ConfigurationError(f"{name} must be greater than zero")
    return value


def _read_optional_int(values: Mapping[str, str], name: str) -> int | None:
    raw_value = values.get(name, "").strip()
    if not raw_value:
        return None
    try:
        value = int(raw_value)
    except ValueError as error:
        raise ConfigurationError(f"{name} must be an integer") from error
    if value < 0:
        raise ConfigurationError(f"{name} cannot be negative")
    return value


@dataclass(frozen=True)
class AppConfig:
    """All settings needed for one assistant session."""

    cohere_api_key: str
    cohere_model: str
    speech_language: str
    tts_language: str
    assistant_language: str
    output_audio: Path
    microphone_index: int | None
    listen_timeout: float
    phrase_time_limit: float

    @property
    def system_prompt(self) -> str:
        return (
            "You are a concise and helpful voice assistant. "
            f"Reply in {self.assistant_language}. Keep answers clear and suitable "
            "for being read aloud."
        )

    @classmethod
    def from_environment(cls, values: Mapping[str, str]) -> "AppConfig":
        api_key = values.get("COHERE_API_KEY", "").strip()
        if not api_key or api_key == "replace_with_your_cohere_api_key":
            raise ConfigurationError(
                "COHERE_API_KEY is missing. Copy config.example.env to .env "
                "and add a valid Cohere API key."
            )

        model = values.get("COHERE_MODEL", "command-a-plus-05-2026").strip()
        if not model:
            raise ConfigurationError("COHERE_MODEL cannot be empty")

        speech_language = values.get("SPEECH_LANGUAGE", "en-US").strip()
        tts_language = values.get("TTS_LANGUAGE", "en").strip()
        assistant_language = values.get("ASSISTANT_LANGUAGE", "English").strip()
        if not all((speech_language, tts_language, assistant_language)):
            raise ConfigurationError("Language settings cannot be empty")

        output_value = values.get(
            "OUTPUT_AUDIO", "output/assistant_response.mp3"
        ).strip()
        if not output_value:
            raise ConfigurationError("OUTPUT_AUDIO cannot be empty")

        return cls(
            cohere_api_key=api_key,
            cohere_model=model,
            speech_language=speech_language,
            tts_language=tts_language,
            assistant_language=assistant_language,
            output_audio=Path(output_value),
            microphone_index=_read_optional_int(values, "MICROPHONE_INDEX"),
            listen_timeout=_read_float(values, "LISTEN_TIMEOUT", 8.0),
            phrase_time_limit=_read_float(values, "PHRASE_TIME_LIMIT", 20.0),
        )

