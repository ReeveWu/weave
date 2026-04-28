"""AI provider integration — multi-provider client, outline generation, and prompts."""

from .outline import (
    expand_all_chapters,
    expand_chapter,
    generate_outline,
    parse_outline_chapters,
)
from .prompts import get_expand_prompt, get_outline_prompt
from .providers.base import AIProvider, B64ImageToken, create_provider


def upload_images(provider: AIProvider, image_filenames: list[str], config) -> dict:
    """Delegate image preparation to the active provider."""
    return provider.upload_images(image_filenames, config)


def cleanup_uploaded_files(provider: AIProvider, uploaded_files: dict) -> None:
    """Delegate cleanup to the active provider."""
    provider.cleanup_uploaded_files(uploaded_files)


__all__ = [
    "AIProvider",
    "B64ImageToken",
    "cleanup_uploaded_files",
    "create_provider",
    "expand_all_chapters",
    "expand_chapter",
    "generate_outline",
    "get_expand_prompt",
    "get_outline_prompt",
    "parse_outline_chapters",
    "upload_images",
]
