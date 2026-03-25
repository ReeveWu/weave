"""Main pipeline orchestration."""

import shutil
from datetime import datetime

from google import genai

from .config import PipelineConfig, console
from .converter import convert_pdfs_to_images, ensure_directories
from .export import convert_to_pdf, post_process
from .ai import cleanup_uploaded_files, upload_images
from .ai import (
    expand_all_chapters,
    generate_outline,
    parse_outline_chapters,
)


def run_pipeline(config: PipelineConfig) -> None:
    """Run the complete lecture-to-handout conversion pipeline."""
    console.print("\n[bold magenta]═══════════════════════════════════[/]")
    console.print("[bold magenta]            Weave            [/]")
    console.print("[bold magenta]═══════════════════════════════════[/]\n")
    console.print(f"[dim]Model: {config.model} | Language: {config.language}[/]\n")

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
        # Step 3: Pass 1 — Outline
        outline = generate_outline(client, uploaded_files, image_filenames, config)

        console.print("[dim]── Outline Preview ──[/]")
        console.print(outline[:2000] + ("..." if len(outline) > 2000 else ""))
        console.print()

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

        # Step 5: Pass 2 — Expand chapters
        full_markdown = expand_all_chapters(
            client, chapters, outline, uploaded_files, config
        )

        # Step 6: Post-processing
        post_process(full_markdown, image_filenames, config)

    finally:
        cleanup_uploaded_files(client, uploaded_files)
        if not config.keep_temp and config.temp_dir.exists():
            shutil.rmtree(str(config.temp_dir), ignore_errors=True)

    # Optional: PDF export
    if config.pdf:
        convert_to_pdf(config)

    console.print("\n[bold green]✨ Handout generation complete![/]")
    console.print(
        f"[dim]Output: {config.output_dir / 'handout.md'}[/]"
    )
    if config.pdf:
        console.print(
            f"[dim]   PDF: {config.output_dir / 'handout.pdf'}[/]"
        )
    console.print()
