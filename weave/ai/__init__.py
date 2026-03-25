"""AI/Gemini integration — API client, outline generation, and prompts."""

from .client import call_gemini, cleanup_uploaded_files, upload_images
from .outline import (
    expand_all_chapters,
    expand_chapter,
    generate_outline,
    parse_outline_chapters,
)
from .prompts import get_expand_prompt, get_outline_prompt

__all__ = [
    "call_gemini",
    "cleanup_uploaded_files",
    "expand_all_chapters",
    "expand_chapter",
    "generate_outline",
    "get_expand_prompt",
    "get_outline_prompt",
    "parse_outline_chapters",
    "upload_images",
]
