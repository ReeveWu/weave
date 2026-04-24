"""Main pipeline orchestration."""

import json
import shutil
import sys
from datetime import datetime

from google import genai

from .ai import (
    cleanup_uploaded_files,
    expand_all_chapters,
    generate_outline,
    parse_outline_chapters,
    upload_images,
)
from .config import PipelineConfig, console
from .converter import convert_pdfs_to_images, ensure_directories
from .export import convert_to_pdf, post_process


def _checkpoint_dir(config: PipelineConfig):
    """Return the checkpoint directory for the current run."""
    return config.output_dir / ".checkpoint"


def _save_checkpoint(config: PipelineConfig, **updates) -> None:
    """Create or update the checkpoint state file."""
    cp_dir = _checkpoint_dir(config)
    cp_dir.mkdir(parents=True, exist_ok=True)
    state_path = cp_dir / "state.json"

    state: dict = {}
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
    state.update(updates)
    state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _load_checkpoint(config: PipelineConfig) -> dict | None:
    """Load checkpoint state, or return ``None`` if not found."""
    state_path = _checkpoint_dir(config) / "state.json"
    if not state_path.exists():
        return None
    return json.loads(state_path.read_text(encoding="utf-8"))


def _save_chapter_content(config: PipelineConfig, idx: int, content: str) -> None:
    """Persist a single expanded chapter to the checkpoint directory."""
    cp_dir = _checkpoint_dir(config)
    cp_dir.mkdir(parents=True, exist_ok=True)
    (cp_dir / f"chapter_{idx:03d}.md").write_text(content, encoding="utf-8")


def _load_chapter_content(config: PipelineConfig, idx: int) -> str | None:
    """Load a previously saved chapter from the checkpoint directory."""
    path = _checkpoint_dir(config) / f"chapter_{idx:03d}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def run_pipeline(config: PipelineConfig) -> None:
    """Run the complete lecture-to-handout conversion pipeline."""
    console.print("\n[bold magenta]═══════════════════════════════════[/]")
    console.print("[bold magenta]            Weave            [/]")
    console.print("[bold magenta]═══════════════════════════════════[/]\n")
    console.print(f"[dim]Model: {config.model} | Language: {config.language}[/]\n")
    console.print(
        "[dim]Retry: "
        f"max={config.max_retries}, "
        f"base={config.retry_base_delay}s, "
        f"503={config.unavailable_retry_delay}s[/]\n"
    )

    resume_mode = config.resume_dir is not None

    if resume_mode:
        config.output_dir = config.resume_dir
        checkpoint = _load_checkpoint(config)
        if not checkpoint or "outline" not in checkpoint:
            console.print(
                "[bold red]Error: No valid checkpoint found in "
                f"{config.resume_dir}[/]\n"
                "[dim]Checkpoint must contain at least a saved outline.[/]"
            )
            sys.exit(1)
        console.print(f"[bold cyan]🔄 Resuming from {config.output_dir}[/]\n")
    else:
        # Step 0: Create a timestamped output sub-folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config.output_dir = config.output_dir / timestamp
        console.print(f"[dim]Output folder: {config.output_dir}[/]\n")

    # Step 0b: Directories
    ensure_directories(config)

    # Step 1: PDF → Images
    image_filenames = convert_pdfs_to_images(config)

    # Step 2: Upload to Gemini
    client = genai.Client(api_key=config.api_key)
    uploaded_files = upload_images(client, image_filenames, config)

    try:
        if resume_mode:
            outline = checkpoint["outline"]
            chapters = checkpoint["chapters"]
            completed_indices = set(checkpoint.get("completed_chapters", []))

            completed_contents: dict[int, str] = {}
            for idx in completed_indices:
                content = _load_chapter_content(config, idx)
                if content:
                    completed_contents[idx] = content

            console.print(
                f"[cyan]📋 {len(chapters)} chapter(s), "
                f"{len(completed_contents)} already expanded[/]\n"
            )
        else:
            # Step 3: Pass 1 — Outline
            outline = generate_outline(client, uploaded_files, image_filenames, config)

            console.print("[dim]── Outline Preview ──[/]")
            console.print(outline[:2000] + ("..." if len(outline) > 2000 else ""))
            console.print()

            # Save checkpoint: outline
            _save_checkpoint(config, outline=outline, image_filenames=image_filenames)

            # Outline-only mode
            if config.outline_only:
                outline_path = config.output_dir / "outline.md"
                outline_path.write_text(outline, encoding="utf-8")
                console.print(f"[bold green]✓ Outline saved to {outline_path}[/]")
                return

            # Step 4: Parse chapters
            chapters = parse_outline_chapters(outline)
            if not chapters:
                console.print(
                    "[yellow]Warning: Could not parse outline into chapters, "
                    "treating as single chapter.[/]"
                )
                chapters = [
                    {
                        "title": "# Complete Handout",
                        "outline_section": outline,
                        "pages": image_filenames,
                    }
                ]

            console.print(f"[cyan]📋 Parsed {len(chapters)} chapter(s)[/]\n")

            # Save checkpoint: chapters
            _save_checkpoint(config, chapters=chapters, completed_chapters=[])
            completed_contents = {}

        # Step 5: Pass 2 — Expand chapters with checkpointing
        def on_chapter_done(idx: int, content: str) -> None:
            _save_chapter_content(config, idx, content)
            state = _load_checkpoint(config) or {}
            completed = state.get("completed_chapters", [])
            if idx not in completed:
                completed.append(idx)
            _save_checkpoint(config, completed_chapters=completed)

        full_markdown = expand_all_chapters(
            client,
            chapters,
            outline,
            uploaded_files,
            config,
            completed_contents=completed_contents,
            on_chapter_done=on_chapter_done,
        )

        # Step 6: Post-processing
        post_process(full_markdown, image_filenames, config)

    except KeyboardInterrupt:
        console.print("\n[bold yellow]Interrupted by user.[/]")
        console.print(
            f"[yellow]Progress saved. Resume with:[/]\n"
            f"[yellow]  weave --resume {config.output_dir} [other options][/]\n"
        )
        cleanup_uploaded_files(client, uploaded_files)
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/]")
        console.print(
            f"[yellow]Progress saved. Resume with:[/]\n"
            f"[yellow]  weave --resume {config.output_dir} [other options][/]\n"
        )
        cleanup_uploaded_files(client, uploaded_files)
        sys.exit(1)

    # Success: clean up everything
    cleanup_uploaded_files(client, uploaded_files)
    if not config.keep_temp and config.temp_dir.exists():
        shutil.rmtree(str(config.temp_dir), ignore_errors=True)

    # Remove checkpoint on success
    cp_dir = _checkpoint_dir(config)
    if cp_dir.exists():
        shutil.rmtree(str(cp_dir), ignore_errors=True)

    # Optional: PDF export
    if config.pdf:
        convert_to_pdf(config)

    console.print("\n[bold green]✨ Handout generation complete![/]")
    console.print(f"[dim]Output: {config.output_dir / 'handout.md'}[/]")
    if config.pdf:
        console.print(f"[dim]   PDF: {config.output_dir / 'handout.pdf'}[/]")
    console.print()
