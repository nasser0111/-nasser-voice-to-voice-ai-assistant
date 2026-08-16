"""Cohere LLM integration."""

from __future__ import annotations

from typing import Any

from .errors import ConfigurationError, ExternalServiceError


class CohereChatModel:
    """Generate conversational responses using Cohere Chat API v2."""

    def __init__(
        self,
        api_key: str,
        model: str,
        system_prompt: str,
        client: Any | None = None,
    ) -> None:
        if not api_key.strip():
            raise ConfigurationError("A Cohere API key is required")
        if not model.strip():
            raise ConfigurationError("A Cohere model name is required")

        if client is None:
            try:
                import cohere
            except ImportError as error:
                raise ConfigurationError(
                    "The cohere package is not installed. Run: "
                    "python -m pip install -r requirements.txt"
                ) from error
            client = cohere.ClientV2(api_key=api_key)

        self._client = client
        self.model = model
        self._system_message = {
            "role": "system",
            "content": system_prompt.strip(),
        }
        self._history: list[dict[str, str]] = []

    def generate(self, user_text: str) -> str:
        prompt = user_text.strip()
        if not prompt:
            raise ValueError("User text cannot be empty")

        messages = [
            self._system_message,
            *self._history,
            {"role": "user", "content": prompt},
        ]
        try:
            response = self._client.chat(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=500,
            )
        except Exception as error:
            raise ExternalServiceError(
                f"Cohere request failed: {error}"
            ) from error

        answer = self._extract_text(response)
        if not answer:
            raise ExternalServiceError("Cohere returned an empty response.")

        self._history.extend(
            [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": answer},
            ]
        )
        # Keep a bounded conversation history: six user/assistant turns.
        self._history = self._history[-12:]
        return answer

    @staticmethod
    def _extract_text(response: Any) -> str:
        message = getattr(response, "message", None)
        if message is None and isinstance(response, dict):
            message = response.get("message")

        content = getattr(message, "content", None)
        if content is None and isinstance(message, dict):
            content = message.get("content")

        if isinstance(content, str):
            return content.strip()
        if not content:
            return ""

        text_parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
            else:
                text = getattr(item, "text", None)
            if text:
                text_parts.append(str(text).strip())
        return "\n".join(part for part in text_parts if part).strip()

