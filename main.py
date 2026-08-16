"""Command-line entry point for the voice-to-voice AI assistant."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from voice_assistant.assistant import VoiceAssistant
from voice_assistant.config import AppConfig
from voice_assistant.errors import VoiceAssistantError
from voice_assistant.llm import CohereChatModel
from voice_assistant.stt import GoogleSpeechToText
from voice_assistant.tts import GoogleTextToSpeech, PlaysoundAudioPlayer

PROJECT_AUTHOR = "Nasser Mamdouh Alshareef"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Speech-to-text, Cohere response generation, and text-to-speech."
    )
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "--text",
        help="Use typed text instead of the microphone (useful for setup tests).",
    )
    input_group.add_argument(
        "--audio-file",
        type=Path,
        help="Transcribe a PCM WAV, AIFF, or FLAC file instead of the microphone.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Override the output MP3 path from the environment file.",
    )
    parser.add_argument(
        "--no-play",
        action="store_true",
        help="Create the response MP3 without playing it automatically.",
    )
    parser.add_argument(
        "--list-microphones",
        action="store_true",
        help="List detected microphones and exit.",
    )
    return parser


def _load_environment_file() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


def _print_microphones() -> int:
    names = GoogleSpeechToText.list_microphones()
    if not names:
        print("No microphones were detected.")
        return 1
    for index, name in enumerate(names):
        print(f"{index}: {name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print(f"Voice-to-Voice AI Assistant | Prepared by {PROJECT_AUTHOR}")
    _load_environment_file()

    try:
        if args.list_microphones:
            return _print_microphones()

        config = AppConfig.from_environment(os.environ)
        output_path = args.output or config.output_audio

        llm = CohereChatModel(
            api_key=config.cohere_api_key,
            model=config.cohere_model,
            system_prompt=config.system_prompt,
        )
        synthesizer = GoogleTextToSpeech(language=config.tts_language)
        player = None if args.no_play else PlaysoundAudioPlayer()

        speech_provider = None
        if args.text is None:
            speech_provider = GoogleSpeechToText(
                language=config.speech_language,
                microphone_index=config.microphone_index,
                listen_timeout=config.listen_timeout,
                phrase_time_limit=config.phrase_time_limit,
            )

        assistant = VoiceAssistant(
            language_model=llm,
            speech_synthesizer=synthesizer,
            speech_provider=speech_provider,
            audio_player=player,
        )

        if args.text is not None:
            result = assistant.process_text(
                args.text, output_path, play_audio=not args.no_play
            )
        elif args.audio_file is not None:
            result = assistant.run_audio_file(
                args.audio_file, output_path, play_audio=not args.no_play
            )
        else:
            result = assistant.run_microphone(
                output_path, play_audio=not args.no_play
            )

        print(f"You said: {result.user_text}")
        print(f"Assistant: {result.assistant_text}")
        print(f"Audio saved to: {result.audio_path.resolve()}")
        return 0
    except (VoiceAssistantError, ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

