"""Anthropic Claude AI provider – Messages API with base64 image blocks."""

from __future__ import annotations

import base64
import time

import anthropic

from ...config import PipelineConfig, console, progress_bar
from .base import AIProvider, B64ImageToken

# Maximum tokens to request from Claude for a single generation.
_MAX_TOKENS = 16384


class ClaudeProvider(AIProvider):
    """Uses the Anthropic Messages API with base64-encoded image source blocks."""

    def __init__(self, api_key: str) -> None:
        self._client = anthropic.Anthropic(api_key=api_key)

    def upload_images(
        self,
        image_filenames: list[str],
        config: PipelineConfig,
    ) -> dict[str, B64ImageToken]:
        """Read images from disk and encode them as base64.

        Claude does not require a separate upload step – images are embedded
        directly in the message payload using the ``base64`` source type.
        """
        console.print("[bold cyan]🖼️  Preparing images for Claude...[/]")
        result: dict[str, B64ImageToken] = {}

        with progress_bar() as progress:
            task = progress.add_task("Loading...", total=len(image_filenames))
            for filename in image_filenames:
                filepath = config.temp_dir / filename
                raw = filepath.read_bytes()
                result[filename] = B64ImageToken(
                    data=base64.b64encode(raw).decode("utf-8"),
                    media_type="image/jpeg",
                )
                progress.update(task, advance=1)

        console.print(f"[bold green]✓ Loaded {len(result)} images[/]\n")
        return result

    def cleanup_uploaded_files(self, uploaded_files: dict) -> None:
        """Nothing to clean up – images were never uploaded remotely."""

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
        """Convert content into Anthropic message blocks and call the API."""
        user_content: list = []
        for item in contents:
            if isinstance(item, str):
                user_content.append({"type": "text", "text": item})
            elif isinstance(item, B64ImageToken):
                user_content.append(
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": item.media_type,
                            "data": item.data,
                        },
                    }
                )

        messages = [{"role": "user", "content": user_content}]

        for attempt in range(max_retries):
            try:
                response = self._client.messages.create(
                    model=model,
                    max_tokens=_MAX_TOKENS,
                    system=system_instruction,
                    messages=messages,
                    temperature=temperature,
                )
                text = response.content[0].text if response.content else ""
                if text:
                    return text
                console.print("[yellow]Warning: Empty response, retrying...[/]")
            except Exception as e:
                if attempt < max_retries - 1:
                    wait = retry_base_delay * (3**attempt)
                    console.print(
                        f"[yellow]API error: {e}, retrying in {wait}s "
                        f"({attempt + 1}/{max_retries})...[/]"
                    )
                    time.sleep(wait)
                else:
                    raise
        return ""
