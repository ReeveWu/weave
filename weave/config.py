"""Shared configuration and utilities."""

from dataclasses import dataclass
from pathlib import Path

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)

console = Console()


@dataclass
class PipelineConfig:
    """Configuration for the lecture conversion pipeline."""

    input_dir: Path
    output_dir: Path
    temp_dir: Path
    model: str = "gemini-2.5-flash"
    api_key: str = ""
    dpi: int = 200
    quality: int = 85
    language: str = "繁體中文"
    keep_temp: bool = False
    outline_only: bool = False
    pdf: bool = False

    @property
    def images_dir(self) -> Path:
        return self.output_dir / "images"


def progress_bar() -> Progress:
    """Create a standardised rich progress bar."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    )
