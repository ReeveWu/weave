"""CLI entry point for Weave."""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console

from . import __version__
from .config import PipelineConfig
from .pipeline import run_pipeline

console = Console()


def main(argv: list[str] | None = None) -> None:
    """Parse arguments and run the conversion pipeline."""
    load_dotenv()

    parser = argparse.ArgumentParser(
        prog="weave",
        description=(
            "Weave — Transform PDF lecture slides into structured "
            "Markdown handouts using multimodal AI (Google Gemini)."
        ),
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=Path("./data"),
        help="Input directory containing PDF files (default: ./data)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("./output"),
        help="Output directory for generated handout (default: ./output)",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default=None,
        help="Gemini model name (default: env GEMINI_MODEL or gemini-2.5-flash)",
    )
    parser.add_argument(
        "-k",
        "--api-key",
        type=str,
        default=None,
        help="Gemini API key (default: env GEMINI_API_KEY)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="DPI for PDF to image conversion (default: 200)",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=85,
        help="JPEG quality 1-100 (default: 85)",
    )
    parser.add_argument(
        "--language",
        type=str,
        default="繁體中文",
        help="Output language for the handout (default: 繁體中文)",
    )
    parser.add_argument(
        "--temp-dir",
        type=Path,
        default=Path("./temp"),
        help="Temporary directory for intermediate files (default: ./temp)",
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep temporary files after processing",
    )
    parser.add_argument(
        "--outline-only",
        action="store_true",
        help="Only generate the outline, skip chapter expansion",
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Also export the handout as PDF (requires weasyprint & markdown)",
    )

    args = parser.parse_args(argv)

    # Resolve API key
    api_key = args.api_key or os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        console.print(
            "[bold red]Error: Gemini API key required.[/]\n"
            "[dim]Set via --api-key, GEMINI_API_KEY env var, or .env file.[/]"
        )
        sys.exit(1)

    # Resolve model
    model = args.model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    config = PipelineConfig(
        input_dir=args.input.resolve(),
        output_dir=args.output.resolve(),
        temp_dir=args.temp_dir.resolve(),
        model=model,
        api_key=api_key,
        dpi=args.dpi,
        quality=args.quality,
        language=args.language,
        keep_temp=args.keep_temp,
        outline_only=args.outline_only,
        pdf=args.pdf,
    )

    run_pipeline(config)


def pdf_main(argv: list[str] | None = None) -> None:
    """Convert an existing Markdown file to PDF."""
    parser = argparse.ArgumentParser(
        prog="weave-pdf",
        description="Convert a Markdown file to PDF.",
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to the Markdown (.md) file to convert",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output PDF path (default: same directory, .pdf extension)",
    )

    args = parser.parse_args(argv)

    md_path = args.input.resolve()
    if not md_path.exists():
        console.print(f"[bold red]Error: file not found: {md_path}[/]")
        sys.exit(1)

    from .export.pdf import convert_md_to_pdf

    console.print("[bold cyan]📑 Converting Markdown to PDF...[/]")
    pdf_path = convert_md_to_pdf(md_path, args.output)
    console.print(f"[bold green]✓ PDF saved to {pdf_path}[/]")
