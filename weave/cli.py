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
        "-p",
        "--provider",
        type=str,
        default=None,
        help="AI provider: gemini, openai, or claude "
        "(default: env WEAVE_PROVIDER or gemini)",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default=None,
        help="Model name (default: env WEAVE_MODEL or provider default)",
    )
    parser.add_argument(
        "-k",
        "--api-key",
        type=str,
        default=None,
        help="API key for the selected provider "
        "(default: env GEMINI_API_KEY / OPENAI_API_KEY / ANTHROPIC_API_KEY)",
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
    parser.add_argument(
        "--max-retries",
        type=int,
        default=None,
        help="Max Gemini retry attempts (default: env WEAVE_MAX_RETRIES or 6)",
    )
    parser.add_argument(
        "--retry-base-delay",
        type=int,
        default=None,
        help="Base retry delay in seconds for general API errors "
        "(default: env WEAVE_RETRY_BASE_DELAY or 2)",
    )
    parser.add_argument(
        "--unavailable-retry-delay",
        type=int,
        default=None,
        help="Minimum retry delay in seconds for Gemini 503/UNAVAILABLE errors "
        "(default: env WEAVE_UNAVAILABLE_RETRY_DELAY or 30)",
    )
    parser.add_argument(
        "--resume",
        type=Path,
        default=None,
        help="Resume from a previous run's output directory "
        "(e.g., output/20260416_150643)",
    )

    args = parser.parse_args(argv)

    # Resolve provider
    provider = args.provider or os.getenv("WEAVE_PROVIDER", "gemini")
    provider = provider.lower()

    # Resolve API key (provider-specific env fallbacks)
    _key_env = {
        "gemini": "GEMINI_API_KEY",
        "openai": "OPENAI_API_KEY",
        "claude": "ANTHROPIC_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
    }
    api_key = args.api_key or os.getenv(_key_env.get(provider, "GEMINI_API_KEY"))
    if not api_key or api_key == "your_api_key_here":
        console.print(
            f"[bold red]Error: API key required for provider '{provider}'.[/]\n"
            f"[dim]Set via --api-key or the corresponding env var "
            f"({_key_env.get(provider, 'GEMINI_API_KEY')}).[/]"
        )
        sys.exit(1)

    # Resolve model (provider defaults)
    _model_defaults = {
        "gemini": "gemini-2.5-flash",
        "openai": "gpt-5.4-mini",
        "claude": "claude-sonnet-4-5",
        "anthropic": "claude-sonnet-4-5",
    }
    model = (
        args.model
        or os.getenv("WEAVE_MODEL")
        or os.getenv("GEMINI_MODEL")  # backward-compat
        or _model_defaults.get(provider, "gemini-2.5-flash")
    )

    max_retries = max(1, int(args.max_retries or os.getenv("WEAVE_MAX_RETRIES", "6")))
    retry_base_delay = max(
        1, int(args.retry_base_delay or os.getenv("WEAVE_RETRY_BASE_DELAY", "2"))
    )
    unavailable_retry_delay = max(
        1,
        int(
            args.unavailable_retry_delay
            or os.getenv("WEAVE_UNAVAILABLE_RETRY_DELAY", "30")
        ),
    )

    config = PipelineConfig(
        input_dir=args.input.resolve(),
        output_dir=args.output.resolve(),
        temp_dir=args.temp_dir.resolve(),
        provider=provider,
        model=model,
        api_key=api_key,
        dpi=args.dpi,
        quality=args.quality,
        language=args.language,
        keep_temp=args.keep_temp,
        outline_only=args.outline_only,
        pdf=args.pdf,
        max_retries=max_retries,
        retry_base_delay=retry_base_delay,
        unavailable_retry_delay=unavailable_retry_delay,
        resume_dir=args.resume.resolve() if args.resume else None,
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
