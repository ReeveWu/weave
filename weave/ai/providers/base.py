"""Abstract AI provider interface and factory."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...config import PipelineConfig


@dataclass
class B64ImageToken:
    """Base64-encoded image token used by OpenAI and Claude providers."""

    data: str  # base64-encoded bytes
    media_type: str = "image/jpeg"


class AIProvider(ABC):
    """Abstract interface that every AI backend must implement."""

    @abstractmethod
    def upload_images(
        self,
        image_filenames: list[str],
        config: PipelineConfig,
    ) -> dict[str, Any]:
        """Prepare images for API use.

        Returns a ``{filename: image_token}`` mapping where the token type
        is provider-specific:
          - Gemini:      google.genai File reference
          - OpenAI/Claude: ``B64ImageToken``
        """
        ...

    @abstractmethod
    def cleanup_uploaded_files(self, uploaded_files: dict[str, Any]) -> None:
        """Release any resources held by uploaded files."""
        ...

    @abstractmethod
    def call(
        self,
        contents: list,
        system_instruction: str,
        model: str,
        temperature: float = 0.5,
        max_retries: int = 6,
        retry_base_delay: int = 2,
        unavailable_retry_delay: int = 30,
    ) -> str:
        """Call the AI API.

        ``contents`` is a flat list whose elements are either plain ``str``
        (text segments) or provider-specific image tokens returned by
        ``upload_images``.  Implementations convert this list into the
        format expected by their respective APIs.
        """
        ...


def create_provider(provider: str, api_key: str) -> AIProvider:
    """Factory – instantiate the right :class:`AIProvider` subclass."""
    if provider == "gemini":
        from .gemini import GeminiProvider

        return GeminiProvider(api_key)
    if provider == "openai":
        from .openai import OpenAIProvider

        return OpenAIProvider(api_key)
    if provider in ("claude", "anthropic"):
        from .claude import ClaudeProvider

        return ClaudeProvider(api_key)
    raise ValueError(
        f"Unknown AI provider {provider!r}. Expected 'gemini', 'openai', or 'claude'."
    )
