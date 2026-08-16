"""Project-specific exceptions."""


class VoiceAssistantError(Exception):
    """Base exception for expected application errors."""


class ConfigurationError(VoiceAssistantError):
    """Raised when configuration or a required dependency is missing."""


class SpeechInputError(VoiceAssistantError):
    """Raised when speech cannot be captured or transcribed."""


class ExternalServiceError(VoiceAssistantError):
    """Raised when an online STT, LLM, or TTS service fails."""


class AudioPlaybackError(VoiceAssistantError):
    """Raised when the generated audio cannot be played."""

