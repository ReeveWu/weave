"""PDF to image conversion utilities."""

import sys

from pdf2image import convert_from_path

from ..config import PipelineConfig, console, progress_bar


def ensure_directories(config: PipelineConfig) -> None:
    """Create all required directories."""
    for d in [config.input_dir, config.output_dir, config.images_dir, config.temp_dir]:
        d.mkdir(parents=True, exist_ok=True)


def convert_pdfs_to_images(config: PipelineConfig) -> list[str]:
    """Convert all PDFs in input directory to JPEG images.

    Returns a list of generated image filenames.
    """
    pdf_files = sorted(config.input_dir.glob("*.pdf"))
    if not pdf_files:
        console.print(
            f"[bold red]Error: No PDF files found in {config.input_dir}[/]"
        )
        sys.exit(1)

    all_filenames: list[str] = []
    console.print(f"\n[bold cyan]📄 Found {len(pdf_files)} PDF file(s)[/]")

    with progress_bar() as progress:
        for pdf_idx, pdf_path in enumerate(pdf_files, start=1):
            task = progress.add_task(f"Converting {pdf_path.name}...", total=None)
            images = convert_from_path(
                str(pdf_path), dpi=config.dpi, fmt="jpeg", thread_count=4,
            )
            progress.update(task, total=len(images))

            for page_idx, image in enumerate(images, start=1):
                filename = f"slide_{pdf_idx:02d}_page_{page_idx:03d}.jpg"
                image.save(
                    str(config.temp_dir / filename), "JPEG", quality=config.quality
                )
                all_filenames.append(filename)
                progress.update(task, advance=1)

    console.print(
        f"[bold green]✓ Converted {len(all_filenames)} slide pages to images[/]\n"
    )
    return all_filenames
