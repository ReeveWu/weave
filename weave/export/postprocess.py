"""Post-processing: image copying, handout saving, coverage verification."""

import re
import shutil

from ..config import PipelineConfig, console


def post_process(
    markdown_content: str,
    all_image_filenames: list[str],
    config: PipelineConfig,
) -> None:
    """Copy referenced images, save handout, and verify slide coverage."""
    console.print("[bold cyan]🔧 Post-processing...[/]")

    # 1. Find referenced images in the Markdown
    ref_pattern = re.compile(r"!\[.*?\]\(\./images/(slide_\d{2}_page_\d{3}\.jpg)\)")
    referenced = set(ref_pattern.findall(markdown_content))

    # 2. Copy referenced images to output
    copied = 0
    for img in referenced:
        src = config.temp_dir / img
        if src.exists():
            shutil.copy2(str(src), str(config.images_dir / img))
            copied += 1
        else:
            console.print(f"[yellow]  Warning: Referenced image {img} not found[/]")

    console.print(f"  📎 Copied {copied} referenced images to output/images/")

    # 3. Save the final Markdown
    output_path = config.output_dir / "handout.md"
    output_path.write_text(markdown_content, encoding="utf-8")
    console.print(f"  📄 Handout saved to {output_path}")

    # 4. Coverage verification
    all_set = set(all_image_filenames)
    page_re = re.compile(r"slide_\d{2}_page_\d{3}\.jpg")
    mentioned = set(page_re.findall(markdown_content))
    missing = all_set - mentioned

    if missing:
        console.print(
            f"\n[yellow]  ⚠ {len(missing)} slide(s) not mentioned in handout:[/]"
        )
        for p in sorted(missing):
            console.print(f"    [dim]{p}[/]")
    else:
        console.print("  [green]✓ All slides covered[/]")
