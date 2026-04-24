"""Gemini API interaction utilities."""

import time

from google import genai
from google.genai import types

from ..config import PipelineConfig, console, progress_bar


def _is_service_unavailable_error(error: Exception) -> bool:
    """Return True when the error looks like a Gemini 503/UNAVAILABLE spike."""
    message = str(error).upper()
    return "503" in message and "UNAVAILABLE" in message


def _get_retry_delay(
    error: Exception,
    attempt: int,
    base_delay: int,
    unavailable_retry_delay: int,
) -> int:
    """Compute retry delay, using a longer floor for 503/UNAVAILABLE errors."""
    wait = base_delay * (3**attempt)
    if _is_service_unavailable_error(error):
        return unavailable_retry_delay + wait
    return wait


def upload_images(
    client: genai.Client,
    image_filenames: list[str],
    config: PipelineConfig,
) -> dict[str, object]:
    """Upload images to Gemini File API. Returns {filename: FileRef} mapping."""
    uploaded: dict[str, object] = {}
    console.print("[bold cyan]☁️  Uploading images to Gemini API...[/]")

    with progress_bar() as progress:
        task = progress.add_task("Uploading...", total=len(image_filenames))
        for filename in image_filenames:
            uploaded[filename] = client.files.upload(
                file=str(config.temp_dir / filename)
            )
            progress.update(task, advance=1)

    console.print("[dim]Waiting for file processing...[/]")
    max_wait = 300
    start = time.time()
    for filename, file_ref in uploaded.items():
        while time.time() - start < max_wait:
            info = client.files.get(name=file_ref.name)
            if info.state and info.state.name == "ACTIVE":
                break
            time.sleep(2)
        else:
            console.print(f"[yellow]Warning: {filename} processing timed out[/]")

    console.print(f"[bold green]✓ Uploaded {len(uploaded)} files[/]\n")
    return uploaded


def call_gemini(
    client: genai.Client,
    contents: list,
    system_instruction: str,
    model: str,
    temperature: float = 0.5,
    max_retries: int = 5,
    retry_base_delay: int = 2,
    unavailable_retry_delay: int = 30,
) -> str:
    """Call Gemini API with automatic retry on failure."""
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=temperature,
                ),
            )
            if response.text:
                return response.text
            console.print("[yellow]Warning: Empty response, retrying...[/]")
        except Exception as e:
            if attempt < max_retries - 1:
                wait = _get_retry_delay(
                    e,
                    attempt,
                    base_delay=retry_base_delay,
                    unavailable_retry_delay=unavailable_retry_delay,
                )
                console.print(
                    f"[yellow]API error: {e}, retrying in {wait}s "
                    f"({attempt + 1}/{max_retries})...[/]"
                )
                time.sleep(wait)
            else:
                raise
    return ""


def cleanup_uploaded_files(
    client: genai.Client, uploaded_files: dict[str, object]
) -> None:
    """Delete uploaded files from Gemini API."""
    console.print("[dim]Cleaning up Gemini uploaded files...[/]")
    for ref in uploaded_files.values():
        try:
            client.files.delete(name=ref.name)
        except Exception:
            pass
