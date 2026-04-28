"""Gemini AI provider – wraps the existing google-genai client utilities."""

from __future__ import annotations

from google import genai

from ...config import PipelineConfig
from ..client import (
    call_gemini,
    cleanup_uploaded_files as _cleanup,
    upload_images as _upload,
)
from .base import AIProvider


class GeminiProvider(AIProvider):
    """Delegates to the existing Gemini File-API / generate_content helpers."""

    def __init__(self, api_key: str) -> None:
        self._client = genai.Client(api_key=api_key)

    def upload_images(
        self, image_filenames: list[str], config: PipelineConfig
    ) -> dict:
        return _upload(self._client, image_filenames, config)

    def cleanup_uploaded_files(self, uploaded_files: dict) -> None:
        _cleanup(self._client, uploaded_files)

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
        return call_gemini(
            self._client,
            contents,
            system_instruction=system_instruction,
            model=model,
            temperature=temperature,
            max_retries=max_retries,
            retry_base_delay=retry_base_delay,
            unavailable_retry_delay=unavailable_retry_delay,
        )
